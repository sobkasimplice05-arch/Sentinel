import json
import re
from pathlib import Path
from typing import Dict, Optional

from loguru import logger
from src.orchestrator.llm_orchestrator import LLMOrchestrator

CODE_BLOCK_RE = re.compile(r"### IMPROVED CODE START\s*(.*?)\s*### IMPROVED CODE END", re.S)


class SelfAudit:
    """Audit autonome des fichiers sources via le LLM local."""

    def __init__(self, orchestrator: LLMOrchestrator):
        self.orchestrator = orchestrator

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
                path.write_text(improved_code, encoding='utf-8')
                result["auto_rewritten"] = True
                result["rewrite_status"] = "Applied improved code"
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
