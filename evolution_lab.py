"""Evolution Lab v2: preuves durables d'autoévolution pour Sentinel.

Le laboratoire sépare l'activité opérationnelle de l'autoévolution de code
réellement démontrée. Il conserve les expériences, transactions, checkpoints et
classes d'erreurs dans la même base SQLite que Sentinel.

Une promotion de code n'est absorbée qu'après une nouvelle invocation qui
observe le commit candidat dans l'historique Git courant. Tant que la preuve
n'est pas observable, l'expérience reste en attente plutôt que d'être déclarée
réussie ou échouée.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EvolutionLab:
    """Enregistre, vérifie et conserve les preuves d'une expérience d'évolution."""

    CODE_ALLOWED_FILES = frozenset(
        {
            "learning_engine.py",
            "feedback_learning.py",
            "autonomy_kernel.py",
            "provider_diagnostics.py",
        }
    )
    MAX_CHANGED_FILES = 2
    MAX_PATTERN_SUMMARY = 240
    MAX_PATTERN_EVIDENCE = 800

    def __init__(
        self,
        db_filename: str | Path = "sentinel_memory.db",
        report_filename: str | Path = "evolution_lab_report.json",
        repo_dir: str | Path = ".",
    ) -> None:
        self.db_filename = Path(db_filename)
        self.report_filename = Path(report_filename)
        self.repo_dir = Path(repo_dir).resolve()
        self._ensure_table()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _fingerprint(text: str) -> str:
        normalized = " ".join(str(text or "").lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

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
                """
                CREATE TABLE IF NOT EXISTS evolution_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    objective_hash TEXT NOT NULL,
                    observation_hash TEXT,
                    base_commit TEXT,
                    base_branch TEXT,
                    candidate_branch TEXT,
                    candidate_commit TEXT,
                    status TEXT NOT NULL,
                    restart_required INTEGER NOT NULL DEFAULT 0,
                    restart_observed_commit TEXT,
                    restart_verified INTEGER NOT NULL DEFAULT 0,
                    outcome TEXT,
                    evidence TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS evolution_checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    objective TEXT,
                    commit_sha TEXT,
                    branch TEXT,
                    baseline_score REAL,
                    candidate_score REAL,
                    measurable_gain INTEGER NOT NULL DEFAULT 0,
                    evidence TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS evolution_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fingerprint TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 1,
                    category TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open'
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_evolution_experiments_cycle ON evolution_experiments(cycle_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_evolution_experiments_decision ON evolution_experiments(decision)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_evolution_transactions_status ON evolution_transactions(status)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_evolution_checkpoints_cycle ON evolution_checkpoints(cycle_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_evolution_patterns_status ON evolution_patterns(status)")
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

    def _git(self, *args: str) -> tuple[int, str, str]:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except (OSError, subprocess.SubprocessError) as exc:
            return 1, "", str(exc)

    def _git_value(self, *args: str) -> str:
        code, stdout, _ = self._git(*args)
        return stdout if code == 0 else ""

    def _is_ancestor(self, ancestor: str, descendant: str) -> bool:
        if not ancestor or not descendant:
            return False
        code, _, _ = self._git("merge-base", "--is-ancestor", ancestor, descendant)
        return code == 0

    def coverage_manifest(self, required_files: Sequence[str] | None = None) -> dict[str, Any]:
        """Produce une couverture déterministe des surfaces candidates.

        Les fichiers présents sont hashés ; les fichiers absents sont explicitement
        signalés. Le manifeste ne lit ni secrets ni workflows.
        """
        files = sorted(set(required_files or self.CODE_ALLOWED_FILES))
        records: list[dict[str, Any]] = []
        omitted: list[dict[str, str]] = []
        for relative in files:
            path = self.repo_dir / relative
            try:
                if not path.is_file():
                    omitted.append({"path": relative, "reason": "missing"})
                    continue
                data = path.read_bytes()
                records.append(
                    {
                        "path": relative,
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                )
            except OSError as exc:
                omitted.append({"path": relative, "reason": f"read_error:{type(exc).__name__}"})
        return {
            "required_files": files,
            "observed_files": records,
            "omitted": omitted,
            "complete": not omitted,
        }

    def start_transaction(
        self,
        *,
        cycle_id: str,
        objective: str,
        observation_hash: str | None,
        candidate_branch: str = "",
    ) -> dict[str, Any]:
        """Démarre ou retrouve une transaction idempotente pour un cycle."""
        objective = str(objective or "").strip() or "autonomous self-improvement"
        now = self._now()
        payload = {
            "cycle_id": str(cycle_id),
            "created_at": now,
            "updated_at": now,
            "objective": objective,
            "objective_hash": self._fingerprint(objective),
            "observation_hash": str(observation_hash or ""),
            "base_commit": self._git_value("rev-parse", "HEAD"),
            "base_branch": self._git_value("rev-parse", "--abbrev-ref", "HEAD"),
            "candidate_branch": str(candidate_branch or ""),
            "status": "started",
            "restart_required": 0,
            "restart_observed_commit": "",
            "restart_verified": 0,
            "outcome": "",
            "evidence": json.dumps({"coverage": self.coverage_manifest()}, ensure_ascii=False, sort_keys=True),
        }
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                INSERT INTO evolution_transactions
                (cycle_id, created_at, updated_at, objective, objective_hash,
                 observation_hash, base_commit, base_branch, candidate_branch, status,
                 restart_required, restart_observed_commit, restart_verified, outcome, evidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cycle_id) DO NOTHING
                """,
                (
                    payload["cycle_id"], payload["created_at"], payload["updated_at"],
                    payload["objective"], payload["objective_hash"], payload["observation_hash"],
                    payload["base_commit"], payload["base_branch"], payload["candidate_branch"],
                    payload["status"], payload["restart_required"], payload["restart_observed_commit"],
                    payload["restart_verified"], payload["outcome"], payload["evidence"],
                ),
            )
            row = connection.execute(
                "SELECT cycle_id, objective, base_commit, base_branch, candidate_branch, status, candidate_commit, restart_verified, outcome FROM evolution_transactions WHERE cycle_id = ?",
                (str(cycle_id),),
            ).fetchone()
        return {
            "cycle_id": row[0],
            "objective": row[1],
            "base_commit": row[2],
            "base_branch": row[3],
            "candidate_branch": row[4],
            "status": row[5],
            "candidate_commit": row[6],
            "restart_verified": bool(row[7]),
            "outcome": row[8],
        }

    def mark_commit(
        self,
        *,
        cycle_id: str,
        candidate_commit: str,
        candidate_branch: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> bool:
        """Marque un commit de code comme candidat, jamais comme absorbé."""
        candidate_commit = str(candidate_commit or "").strip()
        if not candidate_commit:
            return False
        now = self._now()
        with sqlite3.connect(self.db_filename) as connection:
            cursor = connection.execute(
                """
                UPDATE evolution_transactions
                SET updated_at = ?, candidate_commit = ?, candidate_branch = ?,
                    status = 'awaiting_review', restart_required = 0,
                    restart_observed_commit = '', restart_verified = 0,
                    outcome = 'awaiting_review', evidence = ?
                WHERE cycle_id = ? AND status IN ('started', 'candidate_verified', 'committed')
                """,
                (
                    now,
                    candidate_commit,
                    str(candidate_branch or ""),
                    json.dumps(dict(evidence or {}), ensure_ascii=False, sort_keys=True),
                    str(cycle_id),
                ),
            )
            connection.commit()
            return cursor.rowcount == 1

    def finish_transaction(
        self,
        *,
        cycle_id: str,
        status: str = "no_op",
        outcome: str = "no_code_absorbed",
        evidence: Mapping[str, Any] | None = None,
    ) -> bool:
        """Ferme explicitement un cycle qui n’a pas produit de code absorbable."""
        if status not in {"no_op", "failed", "blocked"}:
            raise ValueError("invalid terminal transaction status")
        with sqlite3.connect(self.db_filename) as connection:
            cursor = connection.execute(
                """
                UPDATE evolution_transactions
                SET updated_at = ?, status = ?, restart_required = 0,
                    outcome = ?, evidence = ?
                WHERE cycle_id = ? AND status = 'started'
                """,
                (
                    self._now(), status, str(outcome or status),
                    json.dumps(dict(evidence or {}), ensure_ascii=False, sort_keys=True),
                    str(cycle_id),
                ),
            )
            connection.commit()
            return cursor.rowcount == 1

    def record_checkpoint(
        self,
        *,
        cycle_id: str,
        kind: str,
        status: str,
        objective: str = "",
        commit_sha: str = "",
        branch: str = "",
        baseline_score: float | None = None,
        candidate_score: float | None = None,
        measurable_gain: bool = False,
        evidence: Mapping[str, Any] | None = None,
    ) -> None:
        """Ajoute un checkpoint append-only sans réécrire l’historique."""
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                INSERT INTO evolution_checkpoints
                (cycle_id, created_at, kind, status, objective, commit_sha, branch,
                 baseline_score, candidate_score, measurable_gain, evidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(cycle_id), self._now(), str(kind or "cycle"), str(status or "unknown"),
                    str(objective or ""), str(commit_sha or ""), str(branch or ""),
                    self._float_or_none(baseline_score), self._float_or_none(candidate_score),
                    int(bool(measurable_gain)), json.dumps(dict(evidence or {}), ensure_ascii=False, sort_keys=True),
                ),
            )
            connection.commit()

    def reconcile_pending(self) -> dict[str, Any]:
        """Réconcilie les commits candidats observables au démarrage courant.

        Un candidat publié sur une branche dédiée reste ``awaiting_review`` tant
        que son commit n’est pas présent dans le HEAD de la branche exécutée.
        Après fusion/reprise sur main, un nouveau cycle l’absorbe de manière
        idempotente. Chaque invocation du worker constitue alors une nouvelle
        observation de processus, sans promotion dans le cycle qui a créé le
        candidat.
        """
        observed = self._git_value("rev-parse", "HEAD")
        branch = self._git_value("rev-parse", "--abbrev-ref", "HEAD")
        absorbed = 0
        pending = 0
        rows: list[dict[str, Any]] = []
        checkpoints: list[dict[str, Any]] = []
        with sqlite3.connect(self.db_filename) as connection:
            transactions = connection.execute(
                """
                SELECT cycle_id, objective, candidate_branch, candidate_commit, status
                FROM evolution_transactions
                WHERE status IN ('awaiting_review', 'committed')
                AND (status = 'awaiting_review' OR restart_required = 1)
                ORDER BY id ASC
                """
            ).fetchall()
            for cycle_id, objective, candidate_branch, candidate_commit, status in transactions:
                if self._is_ancestor(str(candidate_commit or ""), observed):
                    now = self._now()
                    connection.execute(
                        """
                        UPDATE evolution_transactions
                        SET updated_at = ?, status = 'absorbed', outcome = 'absorbed',
                            restart_required = 0, restart_observed_commit = ?, restart_verified = 1
                        WHERE cycle_id = ? AND status IN ('awaiting_review', 'committed')
                        """,
                        (now, observed, cycle_id),
                    )
                    checkpoints.append({
                        "cycle_id": cycle_id,
                        "objective": objective,
                        "commit_sha": candidate_commit,
                        "branch": branch or candidate_branch,
                    })
                    absorbed += 1
                    rows.append({"cycle_id": cycle_id, "status": "absorbed", "candidate_commit": candidate_commit})
                else:
                    connection.execute(
                        "UPDATE evolution_transactions SET updated_at = ?, restart_observed_commit = ?, outcome = 'awaiting_review' WHERE cycle_id = ?",
                        (self._now(), observed, cycle_id),
                    )
                    pending += 1
                    rows.append({"cycle_id": cycle_id, "status": "awaiting_review", "candidate_commit": candidate_commit})
            connection.commit()
        for checkpoint in checkpoints:
            self.record_checkpoint(
                cycle_id=checkpoint["cycle_id"],
                kind="restart_reconcile",
                status="absorbed",
                objective=checkpoint["objective"],
                commit_sha=checkpoint["commit_sha"],
                branch=checkpoint["branch"],
                measurable_gain=True,
                evidence={"observed_commit": observed, "observed_branch": branch, "restart_verified": True},
            )
        return {"observed_commit": observed, "observed_branch": branch, "absorbed": absorbed, "pending": pending, "transactions": rows}

    def record_pattern(
        self,
        *,
        summary: str,
        category: str = "process",
        evidence: str = "",
    ) -> dict[str, Any]:
        """Enregistre une classe d’erreur récurrente sans perdre les occurrences."""
        summary = " ".join(str(summary or "").split())[: self.MAX_PATTERN_SUMMARY]
        category = " ".join(str(category or "process").split())[:80] or "process"
        evidence = " ".join(str(evidence or "").split())[: self.MAX_PATTERN_EVIDENCE]
        if not summary:
            return {"recorded": False, "reason": "empty_summary"}
        fingerprint = self._fingerprint(f"{category}|{summary}")
        now = self._now()
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                INSERT INTO evolution_patterns
                (fingerprint, created_at, last_seen, count, category, summary, evidence, status)
                VALUES (?, ?, ?, 1, ?, ?, ?, 'open')
                ON CONFLICT(fingerprint) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    count = evolution_patterns.count + 1,
                    evidence = excluded.evidence,
                    status = 'open'
                """,
                (fingerprint, now, now, category, summary, evidence),
            )
            row = connection.execute(
                "SELECT fingerprint, count, category, summary, status FROM evolution_patterns WHERE fingerprint = ?",
                (fingerprint,),
            ).fetchone()
            connection.commit()
        return {"recorded": True, "fingerprint": row[0], "count": row[1], "category": row[2], "summary": row[3], "status": row[4]}

    def pattern_digest(self, limit: int = 8) -> str:
        with sqlite3.connect(self.db_filename) as connection:
            rows = connection.execute(
                "SELECT fingerprint, count, category, summary FROM evolution_patterns WHERE status = 'open' ORDER BY count DESC, last_seen DESC LIMIT ?",
                (max(1, int(limit)),),
            ).fetchall()
        if not rows:
            return "(no recurring error class recorded)"
        return "\n".join(f"- [{fingerprint}] count={count} category={category}: {summary}" for fingerprint, count, category, summary in rows)

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
        coverage = report.get("coverage") if isinstance(report.get("coverage"), Mapping) else self.coverage_manifest(changed_files or None)

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
            elif not bool(coverage.get("complete")):
                decision = "REJECTED_INCOMPLETE_COVERAGE"
                rejection_reason = "promotion annoncée avec couverture de revue incomplète"

        if code_candidate and original_decision not in {"PROMOTED", "ALREADY_LEARNED"} and not rejection_reason:
            rejection_reason = "candidat non promu"

        evidence = {
            "original_decision": original_decision,
            "tests_passed": tests_passed,
            "measurable_gain": measurable_gain,
            "changed_files": changed_files,
            "coverage": dict(coverage),
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

        if code_candidate and decision not in {"PROMOTED", "ALREADY_LEARNED"} and rejection_reason:
            self.record_pattern(
                summary=str(rejection_reason or "code promotion rejected"),
                category=f"{kind}_promotion",
                evidence=f"cycle={cycle_id}; changed_files={changed_files}; baseline={baseline_score}; candidate={candidate_score}",
            )

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
            "coverage_complete": bool(coverage.get("complete")) if isinstance(coverage, Mapping) else False,
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
            absorbed = connection.execute(
                "SELECT COUNT(*) FROM evolution_transactions WHERE status = 'absorbed'"
            ).fetchone()[0]
            pending = connection.execute(
                "SELECT COUNT(*) FROM evolution_transactions WHERE status = 'committed'"
            ).fetchone()[0]
            awaiting_review = connection.execute(
                "SELECT COUNT(*) FROM evolution_transactions WHERE status = 'awaiting_review'"
            ).fetchone()[0]
            open_patterns = connection.execute(
                "SELECT COUNT(*) FROM evolution_patterns WHERE status = 'open'"
            ).fetchone()[0]
            latest = connection.execute(
                "SELECT cycle_id, created_at, decision FROM evolution_experiments ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return {
            "total_experiments": total,
            "verified_code_promotions": code_promotions,
            "rejected_no_measurement": no_measurement,
            "absorbed_after_restart": absorbed,
            "pending_restart_verification": pending,
            "awaiting_review": awaiting_review,
            "open_error_patterns": open_patterns,
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
            "version": 2,
            "cycle_id": cycle_id,
            "created_at": self._now(),
            "experiments": experiments,
            "pattern_digest": self.pattern_digest(),
            "summary": self.summary(),
            "invariants": [
                "une promotion de code exige un diff non vide",
                "une promotion de code exige une validation réussie",
                "une promotion de code exige candidate_score > baseline_score",
                "une adaptation de politique ne compte pas comme mutation de code",
                "un commit candidat n'est absorbé qu'après vérification au redémarrage",
                "les classes d'erreurs sont conservées par fingerprint et récurrence",
            ],
        }
        self.report_filename.parent.mkdir(parents=True, exist_ok=True)
        self.report_filename.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report


__all__ = ["EvolutionLab"]
