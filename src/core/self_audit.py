import json
import os
import re
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any

from loguru import logger
from src.orchestrator.llm_orchestrator import LLMOrchestrator

CODE_BLOCK_RE = re.compile(r"### IMPROVED CODE START\s*(.*?)\s*### IMPROVED CODE END", re.S)


class SelfAudit:
    """Audit autonome des fichiers sources via le LLM local."""

    def __init__(self, orchestrator: LLMOrchestrator):
        self.orchestrator = orchestrator
        self.repo_root = Path(__file__).resolve().parents[2]
        self.history_dir = self.repo_root / "logs" / "audit_history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.logging_dir = self.repo_root / "logs"

    def _build_audit_prompt(self, file_path: str, source: str) -> str:
        return (
            "You are a local code security auditor. "
            "Review the following Python source file and identify security, correctness, and structure issues. "
            "If you find a safe improvement, return the improved file content between the markers:\n"
            "### IMPROVED CODE START\n<code>\n### IMPROVED CODE END\n"
            "If no change is needed, reply with 'NO_CHANGE_REQUIRED'.\n"
            f"File: {file_path}\n"
            "Source:\n" + source
        )

    def _extract_improved_code(self, response: str) -> Optional[str]:
        match = CODE_BLOCK_RE.search(response)
        if match:
            return match.group(1).strip()
        return None

    def _validate_python_code(self, code: str) -> bool:
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    def _archive_code(self, file_path: Path, code: str) -> Path:
        timestamp = int(time.time())
        archive_file = self.history_dir / f"{file_path.name}.{timestamp}.bak"
        archive_file.write_text(code, encoding='utf-8')
        logger.info(f"   ✅ Archived original code to {archive_file}")
        return archive_file

    def _collect_transparency_anomalies(self) -> Dict[str, Any]:
        anomalies = {
            "error_logs": [],
            "slow_executions": [],
            "quality_fails": [],
            "summary": "",
        }

        if not self.logging_dir.exists():
            return anomalies

        for log_file in sorted(self.logging_dir.glob("*.json"), reverse=True)[:20]:
            try:
                entry = json.loads(log_file.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                continue

            if entry.get("execution", {}).get("model_used") and entry.get("quality", {}).get("status") not in ("PASS", "SUCCESS", "OK"):
                anomalies["quality_fails"].append(log_file.name)

            exec_time = entry.get("execution", {}).get("execution_time_seconds")
            if isinstance(exec_time, (int, float)) and exec_time > 30:
                anomalies["slow_executions"].append({"file": log_file.name, "execution_time": exec_time})

            if entry.get("error"):
                anomalies["error_logs"].append({"file": log_file.name, "error": entry.get("error")})

        anomaly_count = sum(len(v) for k, v in anomalies.items() if k != "summary")
        anomalies["summary"] = f"Detected {anomaly_count} transparency anomalies across recent logs."
        return anomalies

    def evaluate_modification(self, old_code: str, new_code: str) -> bool:
        """Valide une modification autonome avec syntaxe, tests et analyse de logs."""
        logger.info("🔁 Evaluating modification feedback loop...")

        if not self._validate_python_code(new_code):
            logger.error("   ❌ New code failed syntax validation")
            return False

        pytest_result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(self.repo_root)},
            timeout=300,
        )

        if pytest_result.returncode != 0:
            logger.error("   ❌ Pytest suite failed after modification")
            logger.error(pytest_result.stdout)
            logger.error(pytest_result.stderr)
            return False

        anomalies = self._collect_transparency_anomalies()
        if anomalies["error_logs"] or anomalies["quality_fails"] or anomalies["slow_executions"]:
            logger.error("   ❌ Transparency anomalies detected after modification")
            logger.error(anomalies["summary"])
            return False

        logger.info("   ✅ Modification validated successfully")
        return True

    def audit_path(self, file_path: str, rewrite: bool = False) -> Dict:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return {"path": file_path, "success": False, "error": "File not found"}

        source = path.read_text(encoding='utf-8')
        prompt = self._build_audit_prompt(file_path, source)

        routing = {
            "selected_model": "qwen2.5:0.5b",
            "secondary_model": "qwen2.5:1.0b",
            "fallback_model": "qwen2.5:1.0b",
            "endpoint": {
                "url": "http://localhost:11434",
                "model_name": "qwen2.5:0.5b",
                "max_tokens": 2000,
            },
            "strategy": "local_audit",
        }

        response = self.orchestrator.execute(routing, prompt)
        result = {
            "path": file_path,
            "success": response.get("success", False),
            "model_used": response.get("model_used"),
            "analysis": response.get("response"),
            "auto_rewritten": False,
        }

        if not response.get("success"):
            return result

        improved_code = self._extract_improved_code(response["response"])
        if improved_code and rewrite:
            if self._validate_python_code(improved_code):
                archived = self._archive_code(path, source)
                path.write_text(improved_code, encoding='utf-8')
                feedback_ok = self.evaluate_modification(source, improved_code)
                if feedback_ok:
                    result["auto_rewritten"] = True
                    result["rewrite_status"] = "Applied improved code and feedback validated"
                else:
                    path.write_text(archived.read_text(encoding='utf-8'), encoding='utf-8')
                    result["auto_rewritten"] = False
                    result["rewrite_status"] = "Rollback executed after feedback failure"
                    failure_info = {
                        "path": file_path,
                        "error": "Modification failed feedback validation",
                        "archive": str(archived),
                    }
                    if hasattr(self.orchestrator, "notify_feedback"):
                        self.orchestrator.notify_feedback(failure_info)
            else:
                result["rewrite_status"] = "Improved code invalid, not applied"
        elif improved_code:
            result["rewrite_status"] = "Improvement available"
        else:
            result["rewrite_status"] = "No improvement suggested"

        return result

    def audit_and_rewrite_path(self, file_path: str) -> Dict:
        return self.audit_path(file_path, rewrite=True)

    def audit_sources(self, source_paths: Optional[list] = None, rewrite: bool = False) -> Dict:
        if source_paths is None:
            return {"success": False, "error": "No source paths provided"}

        results = []
        for source_path in source_paths:
            results.append(self.audit_path(source_path, rewrite=rewrite))

        return {"success": True, "results": results}
