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
        self.max_prompt_chars = int(os.getenv("SELF_MODIFICATION_PROMPT_CHARS", "24000"))
        self.default_output_tokens = int(os.getenv("SELF_MODIFICATION_MAX_OUTPUT_TOKENS", "4096"))
        self.retry_output_tokens = (self.default_output_tokens, max(2048, self.default_output_tokens // 2), 1024)
        self.max_targets_per_cycle = max(1, int(os.getenv("SELF_MODIFICATION_MAX_TARGETS_PER_CYCLE", "1")))
        self.cooldown_filename = self.root / "self_modification_provider_cooldown.json"
        self.cooldown_seconds = max(60, int(os.getenv("SELF_MODIFICATION_COOLDOWN_SECONDS", "1800")))

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
        *,
        target_file: str | None = None,
        compact: bool = False,
    ) -> str:
        selected = {target_file: sources[target_file]} if target_file and target_file in sources else dict(sources)
        source_text = "\n\n".join(f"### FILE: {name}\n{content}" for name, content in selected.items())
        feedback_limit = 1800 if compact else 3500
        autonomy_limit = 1400 if compact else 2600
        source_limit = max(4000, self.max_prompt_chars - feedback_limit - autonomy_limit - 2600)
        source_text = source_text[:source_limit]
        truncation_note = "Le code affiché est complet." if len(source_text) < source_limit else "Le code est tronqué; retourne files=[] plutôt qu'un fichier incomplet."
        return f"""Tu es le générateur de candidats de Sentinel.

Objectif : proposer au maximum deux améliorations de code limitées aux fichiers autorisés.
Ne modifie jamais les workflows, les secrets, les permissions, les commandes système,
les mécanismes de rollback, les tests de sécurité ou les règles d'intégrité.

Retourne uniquement un JSON valide, sans Markdown ni texte avant ou après, de la forme :
{{
  "hypothesis": "hypothèse falsifiable",
  "expected_gain": "métrique attendue et seuil",
  "files": [{{"path": "learning_engine.py", "content": "contenu Python complet"}}]
}}

Si aucune amélioration justifiée n'est possible, retourne files=[] et explique pourquoi.

Dernier feedback :
{json.dumps(dict(feedback), ensure_ascii=False, separators=(",", ":"))[:feedback_limit]}

État stratégique :
{json.dumps(dict(autonomy), ensure_ascii=False, separators=(",", ":"))[:autonomy_limit]}

Fichier cible : {target_file or 'sélectionner un fichier autorisé'}
Fichiers autorisés : {sorted(self.allowed_files)}

Code actuel :
{source_text}

{truncation_note}
"""

    def _load_cooldowns(self) -> dict[str, float]:
        try:
            payload = json.loads(self.cooldown_filename.read_text(encoding="utf-8"))
            return {str(key): float(value) for key, value in payload.items()}
        except (OSError, ValueError, TypeError):
            return {}

    def _save_cooldowns(self, cooldowns: Mapping[str, float]) -> None:
        self.cooldown_filename.write_text(
            json.dumps(dict(cooldowns), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _provider_on_cooldown(self, provider: str) -> bool:
        return self._load_cooldowns().get(provider.lower(), 0.0) > datetime.now(timezone.utc).timestamp()

    def _set_provider_cooldown(self, provider: str, retry_after: int | None = None) -> None:
        seconds = max(60, min(3600, retry_after or self.cooldown_seconds))
        cooldowns = self._load_cooldowns()
        cooldowns[provider.lower()] = datetime.now(timezone.utc).timestamp() + seconds
        self._save_cooldowns(cooldowns)

    def _call_provider(self, prompt: str, *, output_tokens: int | None = None) -> tuple[str | None, str]:
        output_tokens = output_tokens or self.default_output_tokens
        requested_provider = (os.getenv("SELF_MODIFICATION_PROVIDER") or "auto").lower()
        configured_url = os.getenv("SELF_MODIFICATION_MODEL_URL") or os.getenv("MODEL_API_URL") or os.getenv("OLLAMA_BASE_URL")
        google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY")
        replicate_token = os.getenv("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_KEY")
        provider = requested_provider
        if provider == "auto":
            candidates: list[str] = []
            if configured_url:
                candidates.append("ollama" if ("/api/generate" in configured_url or "11434" in configured_url or os.getenv("OLLAMA_BASE_URL")) else "generic")
            if os.getenv("NVIDIA_API_KEY"):
                candidates.append("nvidia")
            if google_key:
                candidates.append("google")
            if os.getenv("GROQ_API_KEY"):
                candidates.append("groq")
            if replicate_token and (os.getenv("REPLICATE_MODEL_VERSION") or os.getenv("REPLICATE_MODEL")):
                candidates.append("replicate")
            if os.getenv("SELF_MODIFICATION_API_KEY") or os.getenv("MODEL_API_KEY"):
                candidates.append("generic")
            if os.getenv("HF_API_KEY"):
                candidates.append("huggingface")
            provider = next((item for item in dict.fromkeys(candidates) if not self._provider_on_cooldown(item)), "")
            if not provider:
                return None, "PROVIDER_COOLDOWN:all"
        elif self._provider_on_cooldown(provider):
            return None, f"PROVIDER_COOLDOWN:{provider.upper()}"

        model = os.getenv("SELF_MODIFICATION_MODEL") or "Qwen/Qwen2.5-Coder-7B-Instruct"
        token = (
            google_key if provider in {"google", "gemini"} else replicate_token if provider == "replicate" else
            os.getenv("SELF_MODIFICATION_API_KEY") or os.getenv("MODEL_API_KEY") or
            os.getenv("GROQ_API_KEY") or os.getenv("NVIDIA_API_KEY") or os.getenv("HF_API_KEY")
        )
        url = configured_url
        if provider in {"google", "gemini"}:
            model = os.getenv("GOOGLE_MODEL") or os.getenv("GEMINI_MODEL") or os.getenv("SELF_MODIFICATION_MODEL") or "gemini-3.5-flash"
            url = os.getenv("GOOGLE_API_URL") or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        elif provider == "replicate":
            url = os.getenv("REPLICATE_API_URL") or "https://api.replicate.com/v1/predictions"
            model = os.getenv("REPLICATE_MODEL") or model
        elif provider == "ollama":
            url = configured_url or os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434/api/generate"
            model = os.getenv("OLLAMA_MODEL") or os.getenv("SELF_MODIFICATION_MODEL") or "qwen2.5-coder:7b"
        elif not url and provider == "groq" and token:
            url = "https://api.groq.com/openai/v1/chat/completions"
            model = os.getenv("SELF_MODIFICATION_MODEL") or "openai/gpt-oss-120b"
        elif not url and provider in {"nvidia", "nim"} and token:
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            model = os.getenv("SELF_MODIFICATION_MODEL") or "qwen/qwen3-coder-480b-a35b-instruct"
        elif not url and token:
            url = f"https://api-inference.huggingface.co/models/{model}"
        if not url or (provider in {"google", "gemini", "replicate"} and not token):
            return None, "MODEL_UNAVAILABLE"

        headers = {"Content-Type": "application/json"}
        if token and provider not in {"google", "gemini"}:
            headers["Authorization"] = f"Bearer {token}"
        try:
            if provider in {"google", "gemini"} or "generativelanguage.googleapis.com" in url:
                headers["x-goog-api-key"] = token or ""
                response = requests.post(
                    url,
                    headers=headers,
                    json={
                        "system_instruction": {"parts": [{"text": "Return only one valid JSON object. Never use Markdown fences."}]},
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": output_tokens,
                            "responseMimeType": "application/json" if os.getenv("SELF_MODIFICATION_JSON_MODE", "true").lower() == "true" else "text/plain",
                        },
                    },
                    timeout=120,
                )
                response.raise_for_status()
                payload = response.json()
                candidates = payload.get("candidates", []) if isinstance(payload, dict) else []
                parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                text = "".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))
                return (text or None), "GOOGLE"

            if provider == "replicate":
                version = os.getenv("REPLICATE_MODEL_VERSION")
                if not version:
                    return None, "MODEL_UNAVAILABLE"
                response = requests.post(
                    url,
                    headers={**headers, "Prefer": "wait=60"},
                    json={"version": version, "input": {"prompt": prompt, "max_new_tokens": output_tokens, "temperature": 0.1}},
                    timeout=120,
                )
                response.raise_for_status()
                payload = response.json()
                output = payload.get("output") if isinstance(payload, dict) else None
                if isinstance(output, list):
                    output = "".join(str(item) for item in output)
                if isinstance(output, str):
                    return output, "REPLICATE"
                return None, "PROVIDER_ERROR:REPLICATE_ASYNC"

            if "/api/generate" in url or "11434" in url:
                endpoint = url if "/api/generate" in url else f"{url.rstrip('/')}/api/generate"
                response = requests.post(endpoint, headers=headers, json={"model": model, "prompt": prompt, "stream": False}, timeout=90)
                response.raise_for_status()
                return response.json().get("response"), "OLLAMA"

            if "/chat/completions" in url or "api.groq.com" in url or "integrate.api.nvidia.com" in url:
                request_payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Return only one valid JSON object. Never use Markdown fences. Escape every newline and quote inside file content."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": output_tokens,
                }
                if os.getenv("SELF_MODIFICATION_JSON_MODE", "true").lower() == "true":
                    request_payload["response_format"] = {"type": "json_object"}
                response = requests.post(url, headers=headers, json=request_payload, timeout=120)
                response.raise_for_status()
                payload = response.json()
                choices = payload.get("choices", []) if isinstance(payload, dict) else []
                if choices and isinstance(choices[0], dict):
                    message = choices[0].get("message", {})
                    if isinstance(message, dict):
                        return message.get("content"), provider.upper() if provider != "auto" else "OPENAI_COMPATIBLE"
                return None, "EMPTY_OPENAI_COMPATIBLE_RESPONSE"

            if "api-inference.huggingface.co" in url:
                response = requests.post(url, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": output_tokens, "temperature": 0.1, "return_full_text": False}}, timeout=120)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                    return payload[0].get("generated_text"), "HUGGINGFACE_INFERENCE"
                if isinstance(payload, dict):
                    return payload.get("generated_text"), "HUGGINGFACE_INFERENCE"
                return None, "EMPTY_HUGGINGFACE_RESPONSE"

            response = requests.post(url, headers=headers, json={"model": model, "prompt": prompt, "temperature": 0.1}, timeout=90)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload.get("response") or payload.get("generated_text") or payload.get("text"), "GENERIC_API"
            return None, "EMPTY_PROVIDER_RESPONSE"
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            if status == 429:
                retry_after = None
                if exc.response is not None:
                    try:
                        retry_after = int(exc.response.headers.get("retry-after", ""))
                    except (ValueError, TypeError):
                        retry_after = None
                self._set_provider_cooldown(provider, retry_after)
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
        candidate = text[start : end + 1]
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError as first_error:
            # Certains modèles renvoient le contenu Python avec des retours à la
            # ligne littéraux dans la chaîne `content`. On ne répare que cette
            # anomalie, en respectant les séquences d’échappement existantes.
            repaired: list[str] = []
            in_string = False
            escaped = False
            for char in candidate:
                if char == '"' and not escaped:
                    in_string = not in_string
                if char == "\n" and in_string:
                    repaired.append("\\n")
                elif char == "\r" and in_string:
                    repaired.append("\\r")
                elif char == "\t" and in_string:
                    repaired.append("\\t")
                else:
                    repaired.append(char)
                escaped = char == "\\" and not escaped
                if char != "\\":
                    escaped = False
            try:
                payload = json.loads("".join(repaired))
            except json.JSONDecodeError:
                raise first_error
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
        attempts: list[dict[str, Any]] = []
        proposal: PatchProposal | None = None
        provider = "MODEL_UNAVAILABLE"
        selected_target: str | None = None
        last_error = "MODEL_UNAVAILABLE"

        for target_file in sorted(sources)[: self.max_targets_per_cycle]:
            for attempt_index, output_tokens in enumerate(self.retry_output_tokens):
                compact = attempt_index > 0
                prompt = self._build_prompt(
                    sources,
                    feedback,
                    autonomy,
                    target_file=target_file,
                    compact=compact,
                )
                raw, provider = self._call_provider(prompt, output_tokens=output_tokens)
                attempt = {
                    "target_file": target_file,
                    "attempt": attempt_index + 1,
                    "compact": compact,
                    "prompt_chars": len(prompt),
                    "output_tokens": output_tokens,
                    "provider": provider,
                }
                attempts.append(attempt)
                if raw is None:
                    last_error = provider
                    if "HTTP_413" in provider:
                        continue
                    break
                try:
                    candidate = self._parse_proposal(raw)
                except ValueError as exc:
                    attempt["parse_error"] = str(exc)[:500]
                    last_error = "INVALID_MODEL_JSON"
                    # Une réponse non structurée rend ce fournisseur impropre à
                    # cette série de tentatives; en mode auto, le prochain essai
                    # peut basculer vers le fournisseur suivant sans attendre le
                    # prochain runner éphémère.
                    if (os.getenv("SELF_MODIFICATION_PROVIDER") or "auto").lower() == "auto" and provider:
                        self._set_provider_cooldown(provider)
                    if attempt_index < len(self.retry_output_tokens) - 1:
                        continue
                    break
                valid_structure, structure_reason = self._validate_structure(candidate)
                if not valid_structure:
                    attempt["structure_reason"] = structure_reason
                    last_error = structure_reason
                    if structure_reason == "NO_CHANGE_PROPOSED":
                        break
                    report = {
                        "cycle_id": cycle_id,
                        "decision": "REJECTED",
                        "provider": provider,
                        "reason": structure_reason,
                        "attempts": attempts,
                        "created_at": self._now(),
                    }
                    self._write_report(report)
                    return report
                proposal = candidate
                selected_target = target_file
                break
            if proposal is not None:
                break

        if proposal is None:
            if last_error == "MODEL_UNAVAILABLE":
                decision = "MODEL_UNAVAILABLE"
            elif last_error == "NO_CHANGE_PROPOSED":
                decision = "NO_CHANGE_PROPOSED"
            else:
                decision = "PROVIDER_ERROR"
            report = {
                "cycle_id": cycle_id,
                "decision": decision,
                "provider": provider,
                "reason": "Aucun fournisseur configuré" if decision == "MODEL_UNAVAILABLE" else last_error,
                "attempts": attempts,
                "created_at": self._now(),
            }
            self._write_report(report)
            return report

        try:
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
                    "target_file": selected_target,
                    "attempts": attempts,
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
                "target_file": selected_target,
                "attempts": attempts,
                "tests": test_details,
                "created_at": self._now(),
            }
            self._write_report(report)
            return report
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            report = {"cycle_id": cycle_id, "decision": "REJECTED", "provider": provider, "reason": str(exc)[:1000], "created_at": self._now()}
            self._write_report(report)
            return report
