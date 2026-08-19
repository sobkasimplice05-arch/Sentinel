#!/usr/bin/env python3
"""Moteur d'auto-modification source de Sentinel.

Le moteur permet à Sentinel de proposer des versions candidates de modules
non structurels, de les tester et de ne promouvoir que celles qui apportent un
changement mesurable. En l'absence de fournisseur de génération configuré, il
produit un état explicite MODEL_UNAVAILABLE plutôt qu'une fausse mutation.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import requests


@dataclass(frozen=True)
class PatchProposal:
    hypothesis: str
    files: dict[str, str]
    expected_gain: str


class SelfModificationEngine:
    """Génère, teste et applique des candidats de code dans un périmètre autorisé."""

    DEFAULT_ALLOWED_FILES = frozenset(
        {
            "learning_engine.py",
            "feedback_learning.py",
            "autonomy_kernel.py",
        }
    )

    def __init__(
        self,
        root: str | Path = ".",
        report_filename: str | Path = "self_modification_report.json",
        allowed_files: set[str] | frozenset[str] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.report_filename = self.root / report_filename
        self.allowed_files = frozenset(allowed_files or self.DEFAULT_ALLOWED_FILES)
        self.max_file_bytes = 120_000
        self.max_changed_files = 2

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _read_sources(self) -> dict[str, str]:
        sources: dict[str, str] = {}
        for relative in sorted(self.allowed_files):
            path = self.root / relative
            if path.exists():
                sources[relative] = path.read_text(encoding="utf-8")
        return sources

    def _build_prompt(
        self,
        sources: Mapping[str, str],
        feedback: Mapping[str, Any],
        autonomy: Mapping[str, Any],
    ) -> str:
        source_text = "\n\n".join(f"### FILE: {name}\n{content}" for name, content in sources.items())
        return f"""Tu es le générateur de candidats de Sentinel.

Objectif : proposer au maximum deux améliorations de code limitées aux fichiers autorisés.
Ne modifie jamais les workflows, les secrets, les permissions, les commandes système,
les mécanismes de rollback, les tests de sécurité ou les règles d'intégrité.

Retourne uniquement un JSON valide de la forme :
{{
  "hypothesis": "hypothèse falsifiable",
  "expected_gain": "métrique attendue et seuil",
  "files": [{{"path": "learning_engine.py", "content": "contenu Python complet"}}]
}}

Si aucune amélioration justifiée n'est possible, retourne files=[] et explique pourquoi.

Dernier feedback :
{json.dumps(dict(feedback), ensure_ascii=False, indent=2)[:12000]}

État stratégique :
{json.dumps(dict(autonomy), ensure_ascii=False, indent=2)[:8000]}

Fichiers autorisés : {sorted(self.allowed_files)}

Code actuel :
{source_text[:36000]}
"""

    def _call_provider(self, prompt: str) -> tuple[str | None, str]:
        provider = (os.getenv("SELF_MODIFICATION_PROVIDER") or "auto").lower()
        if provider == "auto":
            if os.getenv("NVIDIA_API_KEY"):
                provider = "nvidia"
            elif os.getenv("GROQ_API_KEY"):
                provider = "groq"
            elif os.getenv("SELF_MODIFICATION_API_KEY") or os.getenv("MODEL_API_KEY"):
                provider = "generic"
            elif os.getenv("HF_API_KEY"):
                provider = "huggingface"
        model = os.getenv("SELF_MODIFICATION_MODEL") or "Qwen/Qwen2.5-Coder-7B-Instruct"
        token = (
            os.getenv("SELF_MODIFICATION_API_KEY")
            or os.getenv("MODEL_API_KEY")
            or os.getenv("GROQ_API_KEY")
            or os.getenv("NVIDIA_API_KEY")
            or os.getenv("HF_API_KEY")
        )
        url = os.getenv("SELF_MODIFICATION_MODEL_URL") or os.getenv("MODEL_API_URL") or os.getenv("OLLAMA_BASE_URL")
        if not url and provider == "groq" and token:
            url = "https://api.groq.com/openai/v1/chat/completions"
            model = os.getenv("SELF_MODIFICATION_MODEL") or "openai/gpt-oss-120b"
        if not url and provider in {"nvidia", "nim"} and token:
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            model = os.getenv("SELF_MODIFICATION_MODEL") or "qwen/qwen3-coder-480b-a35b-instruct"
        if not url and token:
            url = f"https://api-inference.huggingface.co/models/{model}"
        if not url:
            return None, "MODEL_UNAVAILABLE"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            if "/api/generate" in url or "11434" in url:
                endpoint = url if "/api/generate" in url else f"{url.rstrip('/')}/api/generate"
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=90,
                )
                response.raise_for_status()
                return response.json().get("response"), "OLLAMA"

            if "/chat/completions" in url or "api.groq.com" in url or "integrate.api.nvidia.com" in url:
                response = requests.post(
                    url,
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "Return only the requested JSON candidate patch."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 16000,
                    },
                    timeout=120,
                )
                response.raise_for_status()
                payload = response.json()
                choices = payload.get("choices", []) if isinstance(payload, dict) else []
                if choices and isinstance(choices[0], dict):
                    message = choices[0].get("message", {})
                    if isinstance(message, dict):
                        return message.get("content"), provider.upper() if provider != "auto" else "OPENAI_COMPATIBLE"
                return None, "EMPTY_OPENAI_COMPATIBLE_RESPONSE"

            if "api-inference.huggingface.co" in url:
                response = requests.post(
                    url,
                    headers=headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 16000,
                            "temperature": 0.1,
                            "return_full_text": False,
                        },
                    },
                    timeout=120,
                )
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                    return payload[0].get("generated_text"), "HUGGINGFACE_INFERENCE"
                if isinstance(payload, dict):
                    return payload.get("generated_text"), "HUGGINGFACE_INFERENCE"
                return None, "EMPTY_HUGGINGFACE_RESPONSE"

            response = requests.post(
                url,
                headers=headers,
                json={"model": model, "prompt": prompt, "temperature": 0.1},
                timeout=90,
            )
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload.get("response") or payload.get("generated_text") or payload.get("text"), "GENERIC_API"
            return None, "EMPTY_PROVIDER_RESPONSE"
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            return None, f"PROVIDER_ERROR:HTTP_{status}"
        except (requests.RequestException, ValueError, TypeError) as exc:
            return None, f"PROVIDER_ERROR:{type(exc).__name__}"

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1])
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("réponse sans objet JSON")
        payload = json.loads(text[start : end + 1])
        if not isinstance(payload, dict):
            raise ValueError("réponse JSON invalide")
        return payload

    def _parse_proposal(self, raw: str | None) -> PatchProposal:
        if not raw:
            raise ValueError("réponse vide")
        payload = self._extract_json(raw)
        entries = payload.get("files", [])
        if not isinstance(entries, list) or len(entries) > self.max_changed_files:
            raise ValueError("nombre de fichiers candidats non autorisé")
        files: dict[str, str] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("entrée de fichier invalide")
            path = entry.get("path")
            content = entry.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                raise ValueError("path/content invalides")
            if path not in self.allowed_files or Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValueError(f"fichier non autorisé: {path}")
            if len(content.encode("utf-8")) > self.max_file_bytes:
                raise ValueError(f"fichier trop volumineux: {path}")
            files[path] = content
        hypothesis = str(payload.get("hypothesis", "hypothèse non fournie"))[:1000]
        expected_gain = str(payload.get("expected_gain", "gain non fourni"))[:1000]
        return PatchProposal(hypothesis=hypothesis, files=files, expected_gain=expected_gain)

    def _validate_structure(self, proposal: PatchProposal) -> tuple[bool, str]:
        if not proposal.files:
            return False, "NO_CHANGE_PROPOSED"
        for path, content in proposal.files.items():
            if "subprocess" in content and path == "learning_engine.py":
                return False, "forbidden_process_control"
            if "os.system(" in content or "git push --force" in content:
                return False, "forbidden_unbounded_side_effect"
            if "SELF_MODIFICATION_MODEL_URL" in content:
                return False, "self_provider_mutation_forbidden"
        return True, "structure_valid"

    def _run_candidate_tests(self, candidate_root: Path, files: Mapping[str, str]) -> tuple[bool, dict[str, Any]]:
        compile_targets = [str(candidate_root / path) for path in files if path.endswith(".py")]
        compile_result = subprocess.run(
            ["python", "-m", "py_compile", *compile_targets],
            cwd=candidate_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        test_result = subprocess.run(
            ["python", "-m", "pytest", "-q", "tests/test_feedback_learning.py", "tests/test_autonomy_kernel.py"],
            cwd=candidate_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        details = {
            "compile_returncode": compile_result.returncode,
            "compile_output": (compile_result.stdout + compile_result.stderr)[-4000:],
            "test_returncode": test_result.returncode,
            "test_output": (test_result.stdout + test_result.stderr)[-6000:],
        }
        return compile_result.returncode == 0 and test_result.returncode == 0, details

    def _score(self, details: Mapping[str, Any], proposal: PatchProposal) -> float:
        if details.get("compile_returncode") != 0 or details.get("test_returncode") != 0:
            return 0.0
        meaningful_change = sum(1 for path, content in proposal.files.items() if content != (self.root / path).read_text(encoding="utf-8"))
        return round(min(1.0, 0.75 + meaningful_change * 0.10), 6)

    def _write_report(self, report: Mapping[str, Any]) -> None:
        self.report_filename.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def run_cycle(
        self,
        *,
        feedback: Mapping[str, Any],
        autonomy: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Propose puis teste un patch; la promotion remplace uniquement les fichiers autorisés."""
        cycle_id = f"self-mod-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        if os.getenv("SELF_MODIFICATION_ENABLED", "true").lower() != "true":
            report = {"cycle_id": cycle_id, "decision": "DISABLED", "created_at": self._now()}
            self._write_report(report)
            return report

        sources = self._read_sources()
        raw, provider = self._call_provider(self._build_prompt(sources, feedback, autonomy))
        if raw is None:
            decision = "MODEL_UNAVAILABLE" if provider == "MODEL_UNAVAILABLE" else "PROVIDER_ERROR"
            report = {
                "cycle_id": cycle_id,
                "decision": decision,
                "provider": provider,
                "reason": "Aucun fournisseur configuré" if decision == "MODEL_UNAVAILABLE" else provider,
                "created_at": self._now(),
            }
            self._write_report(report)
            return report
        try:
            proposal = self._parse_proposal(raw)
            valid_structure, structure_reason = self._validate_structure(proposal)
            if not valid_structure:
                report = {"cycle_id": cycle_id, "decision": "REJECTED", "provider": provider, "reason": structure_reason, "created_at": self._now()}
                self._write_report(report)
                return report

            with tempfile.TemporaryDirectory(prefix="sentinel-candidate-") as directory:
                candidate_root = Path(directory)
                shutil.copytree(self.root, candidate_root, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
                for path, content in proposal.files.items():
                    destination = candidate_root / path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(content, encoding="utf-8")
                passed, test_details = self._run_candidate_tests(candidate_root, proposal.files)
                score = self._score(test_details, proposal)

            baseline_score = 0.75
            if not passed or score <= baseline_score:
                report = {
                    "cycle_id": cycle_id,
                    "decision": "REJECTED",
                    "provider": provider,
                    "hypothesis": proposal.hypothesis,
                    "expected_gain": proposal.expected_gain,
                    "baseline_score": baseline_score,
                    "candidate_score": score,
                    "tests": test_details,
                    "created_at": self._now(),
                }
                self._write_report(report)
                return report

            for path, content in proposal.files.items():
                (self.root / path).write_text(content, encoding="utf-8")
            report = {
                "cycle_id": cycle_id,
                "decision": "PROMOTED",
                "provider": provider,
                "hypothesis": proposal.hypothesis,
                "expected_gain": proposal.expected_gain,
                "baseline_score": baseline_score,
                "candidate_score": score,
                "changed_files": sorted(proposal.files),
                "tests": test_details,
                "created_at": self._now(),
            }
            self._write_report(report)
            return report
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            report = {"cycle_id": cycle_id, "decision": "REJECTED", "provider": provider, "reason": str(exc)[:1000], "created_at": self._now()}
            self._write_report(report)
            return report
