"""Curriculum d’auto-évolution source à coût nul et à promotion contrôlée.

Le curriculum est volontairement limité à des micro-évolutions utiles et
réversibles. Il ne modifie ni les workflows, ni les secrets, ni les permissions,
ni les garde-fous de Sentinel. Une évolution est promue seulement si le candidat
surpasse la baseline sur deux variantes de transfert dans une copie isolée.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


TASK_NAME = "compact_http_413_recovery"
TARGET_FILE = "provider_diagnostics.py"
EXPECTED_ACTION = "shrink_prompt_then_retry"
TRANSFER_VARIANTS = ("PROVIDER_ERROR:HTTP_413", "HTTP_413:oversized_prompt")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _score_root(root: Path, variants: Sequence[str]) -> tuple[float, dict[str, bool]]:
    checks: dict[str, bool] = {}
    for variant in variants:
        code = (
            "from provider_diagnostics import classify_provider_status; "
            f"raise SystemExit(0 if classify_provider_status({variant!r}) == {EXPECTED_ACTION!r} else 1)"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=root, capture_output=True, text=True, timeout=20
        )
        checks[variant] = result.returncode == 0
    score = round(sum(checks.values()) / len(checks), 6) if checks else 0.0
    return score, checks


def _candidate_content(source: str) -> str | None:
    if EXPECTED_ACTION in source:
        return None
    anchor = '    if "INVALID_MODEL_JSON" in normalized:\n'
    addition = '    if "HTTP_413" in normalized:\n        return "shrink_prompt_then_retry"\n'
    if anchor not in source:
        raise ValueError("ancre de curriculum introuvable")
    return source.replace(anchor, addition + anchor, 1)


def run_source_evolution_curriculum(
    root: str | Path = ".",
    report_filename: str | Path = "source_evolution_report.json",
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    target = root_path / TARGET_FILE
    report_path = root_path / report_filename
    source = target.read_text(encoding="utf-8") if target.exists() else ""
    report: dict[str, Any] = {
        "task": TASK_NAME,
        "target_file": TARGET_FILE,
        "created_at": _now(),
        "transfer_variants": list(TRANSFER_VARIANTS),
        "constraints": [
            "aucun workflow, secret, permission ou garde-fou modifié",
            "compilation et transfert isolés requis",
            "candidate_score strictement supérieur à baseline_score",
        ],
    }
    candidate = _candidate_content(source)
    if candidate is None:
        report.update({"decision": "ALREADY_LEARNED", "changed_files": [], "reason": "compétence déjà présente"})
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    baseline_score, baseline_cases = _score_root(root_path, TRANSFER_VARIANTS)
    with tempfile.TemporaryDirectory(prefix="sentinel-curriculum-") as directory:
        candidate_root = Path(directory) / "candidate"
        shutil.copytree(root_path, candidate_root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        candidate_target = candidate_root / TARGET_FILE
        candidate_target.write_text(candidate, encoding="utf-8")
        compile_result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(candidate_target)],
            cwd=candidate_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        candidate_score, candidate_cases = _score_root(candidate_root, TRANSFER_VARIANTS)
        tests_passed = compile_result.returncode == 0 and candidate_score > baseline_score
        report.update(
            {
                "baseline_score": baseline_score,
                "candidate_score": candidate_score,
                "baseline_cases": baseline_cases,
                "candidate_cases": candidate_cases,
                "compile_returncode": compile_result.returncode,
                "compile_output": (compile_result.stdout + compile_result.stderr)[-1000:],
            }
        )
        if tests_passed:
            target.write_text(candidate, encoding="utf-8")
            report.update(
                {
                    "decision": "PROMOTED",
                    "changed_files": [TARGET_FILE],
                    "reason": "gain mesuré sur variantes inédites et compilation isolée réussie",
                }
            )
        else:
            report.update(
                {
                    "decision": "REJECTED",
                    "changed_files": [],
                    "reason": "le candidat ne dépasse pas la baseline ou ne compile pas",
                }
            )
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


__all__ = ["run_source_evolution_curriculum"]
