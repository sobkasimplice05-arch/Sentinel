"""Registre et garde-fou d'Evolution Lab v1.

Le laboratoire sépare l'activité opérationnelle de l'autoévolution de code
réellement démontrée. Il conserve les expériences et leurs échecs dans la même
base SQLite que Sentinel, sans donner au générateur accès aux secrets ou aux
workflows.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


class EvolutionLab:
    """Enregistre et qualifie les preuves d'une expérience d'évolution."""

    CODE_ALLOWED_FILES = frozenset(
        {
            "learning_engine.py",
            "feedback_learning.py",
            "autonomy_kernel.py",
            "provider_diagnostics.py",
        }
    )
    MAX_CHANGED_FILES = 2

    def __init__(
        self,
        db_filename: str | Path = "sentinel_memory.db",
        report_filename: str | Path = "evolution_lab_report.json",
    ) -> None:
        self.db_filename = Path(db_filename)
        self.report_filename = Path(report_filename)
        self._ensure_table()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _ensure_table(self) -> None:
        self.db_filename.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS evolution_experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    observation_hash TEXT,
                    hypothesis TEXT,
                    expected_gain TEXT,
                    base_commit TEXT,
                    candidate_branch TEXT,
                    candidate_commit TEXT,
                    changed_files TEXT NOT NULL,
                    tests_passed INTEGER NOT NULL,
                    baseline_score REAL,
                    candidate_score REAL,
                    decision TEXT NOT NULL,
                    rejection_reason TEXT,
                    model_used TEXT,
                    evidence TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_evolution_experiments_cycle ON evolution_experiments(cycle_id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_evolution_experiments_decision ON evolution_experiments(decision)"
            )
            connection.commit()

    @staticmethod
    def _float_or_none(value: Any) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _changed_files(report: Mapping[str, Any]) -> list[str]:
        value = report.get("changed_files", [])
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
            return []
        return sorted({str(item) for item in value if isinstance(item, str) and item})

    @staticmethod
    def _tests_passed(report: Mapping[str, Any]) -> bool:
        tests = report.get("tests")
        if isinstance(tests, Mapping):
            required = ("compile_returncode", "test_returncode")
            return all(key in tests and tests.get(key) == 0 for key in required)
        compile_returncode = report.get("compile_returncode")
        transfer_cases = report.get("candidate_cases")
        if compile_returncode is not None and isinstance(transfer_cases, Mapping):
            return compile_returncode == 0 and bool(transfer_cases) and all(bool(value) for value in transfer_cases.values())
        return False

    def record_experiment(
        self,
        *,
        cycle_id: str,
        observation_hash: str | None,
        kind: str,
        report: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Conserve une expérience et refuse les promotions de code non prouvées."""
        kind = str(kind or "unknown")[:64]
        original_decision = str(report.get("decision", "UNKNOWN"))
        changed_files = self._changed_files(report)
        baseline_score = self._float_or_none(report.get("baseline_score"))
        candidate_score = self._float_or_none(report.get("candidate_score"))
        tests_passed = self._tests_passed(report)
        code_candidate = kind in {"self_modification", "source_evolution"}
        measurable_gain = (
            baseline_score is not None
            and candidate_score is not None
            and candidate_score > baseline_score
        )
        rejection_reason = report.get("reason") or report.get("rejection_reason")
        decision = original_decision

        if code_candidate and original_decision == "PROMOTED":
            unauthorized = [path for path in changed_files if path not in self.CODE_ALLOWED_FILES]
            if not changed_files:
                decision = "REJECTED_NO_DIFF"
                rejection_reason = "promotion annoncée sans diff de code"
            elif len(changed_files) > self.MAX_CHANGED_FILES or unauthorized:
                decision = "REJECTED_FORBIDDEN_DIFF"
                rejection_reason = "diff hors périmètre ou trop volumineux"
            elif not tests_passed:
                decision = "REJECTED_VALIDATION"
                rejection_reason = "promotion annoncée sans validation complète"
            elif not measurable_gain:
                decision = "REJECTED_NO_MEASUREMENT"
                rejection_reason = "promotion annoncée sans gain strictement supérieur à la baseline"

        if code_candidate and original_decision not in {"PROMOTED", "ALREADY_LEARNED"} and not rejection_reason:
            rejection_reason = "candidat non promu"

        evidence = {
            "original_decision": original_decision,
            "tests_passed": tests_passed,
            "measurable_gain": measurable_gain,
            "changed_files": changed_files,
            "report": dict(report),
        }
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                INSERT INTO evolution_experiments
                (cycle_id, created_at, kind, observation_hash, hypothesis, expected_gain,
                 base_commit, candidate_branch, candidate_commit, changed_files, tests_passed,
                 baseline_score, candidate_score, decision, rejection_reason, model_used, evidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cycle_id,
                    self._now(),
                    kind,
                    observation_hash,
                    str(report.get("hypothesis", ""))[:2000],
                    str(report.get("expected_gain", ""))[:2000],
                    report.get("base_commit"),
                    report.get("candidate_branch"),
                    report.get("candidate_commit"),
                    json.dumps(changed_files, ensure_ascii=False),
                    int(tests_passed),
                    baseline_score,
                    candidate_score,
                    decision,
                    str(rejection_reason)[:2000] if rejection_reason else None,
                    report.get("provider") or report.get("model_used"),
                    json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                ),
            )
            connection.commit()

        return {
            "cycle_id": cycle_id,
            "kind": kind,
            "decision": decision,
            "original_decision": original_decision,
            "code_promotion_verified": code_candidate and decision == "PROMOTED",
            "changed_files": changed_files,
            "tests_passed": tests_passed,
            "baseline_score": baseline_score,
            "candidate_score": candidate_score,
            "measurable_gain": measurable_gain,
            "rejection_reason": rejection_reason,
        }

    def summary(self) -> dict[str, Any]:
        with sqlite3.connect(self.db_filename) as connection:
            total = connection.execute("SELECT COUNT(*) FROM evolution_experiments").fetchone()[0]
            code_promotions = connection.execute(
                "SELECT COUNT(*) FROM evolution_experiments WHERE decision = 'PROMOTED' AND kind IN ('self_modification', 'source_evolution')"
            ).fetchone()[0]
            no_measurement = connection.execute(
                "SELECT COUNT(*) FROM evolution_experiments WHERE decision = 'REJECTED_NO_MEASUREMENT'"
            ).fetchone()[0]
            latest = connection.execute(
                "SELECT cycle_id, created_at, decision FROM evolution_experiments ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return {
            "total_experiments": total,
            "verified_code_promotions": code_promotions,
            "rejected_no_measurement": no_measurement,
            "latest": {
                "cycle_id": latest[0],
                "created_at": latest[1],
                "decision": latest[2],
            } if latest else None,
        }

    def record_cycle(
        self,
        *,
        cycle_id: str,
        observation_hash: str | None,
        feedback_report: Mapping[str, Any],
        self_modification_report: Mapping[str, Any],
        source_evolution_report: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Enregistre séparément la politique et les deux voies de code."""
        experiments = [
            self.record_experiment(
                cycle_id=cycle_id,
                observation_hash=observation_hash,
                kind="policy",
                report=feedback_report,
            ),
            self.record_experiment(
                cycle_id=cycle_id,
                observation_hash=observation_hash,
                kind="self_modification",
                report=self_modification_report,
            ),
            self.record_experiment(
                cycle_id=cycle_id,
                observation_hash=observation_hash,
                kind="source_evolution",
                report=source_evolution_report,
            ),
        ]
        report = {
            "version": 1,
            "cycle_id": cycle_id,
            "created_at": self._now(),
            "experiments": experiments,
            "summary": self.summary(),
            "invariants": [
                "une promotion de code exige un diff non vide",
                "une promotion de code exige une validation réussie",
                "une promotion de code exige candidate_score > baseline_score",
                "une adaptation de politique ne compte pas comme mutation de code",
            ],
        }
        self.report_filename.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report


__all__ = ["EvolutionLab"]
