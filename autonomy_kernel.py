#!/usr/bin/env python3
"""Noyau d'autonomie maximale contrôlée pour Sentinel.

Ce module donne à Sentinel une mémoire stratégique et la capacité de choisir
son prochain travail à partir des résultats précédents, sans exécuter de code
arbitraire ni modifier les garde-fous structurels.
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Literal

DEFAULT_STATE: dict[str, Any] = {
    "version": 1,
    "autonomy_mode": "MAXIMUM_CONTROLLED",
    "cycle_number": 0,
    "total_plans": 0,
    "successful_experiments": 0,
    "rejected_experiments": 0,
    "last_observation_hash": None,
    "active_objectives": [
        "improve_observation_quality",
        "improve_source_reliability",
        "preserve_structural_integrity",
    ],
    "capabilities": [
        "observe_external_sources",
        "maintain_long_term_memory",
        "plan_next_action",
        "adapt_runtime_policy",
        "evaluate_feedback",
        "self_diagnose_failures",
    ],
    "strategy": {
        "name": "evidence_driven_adaptation",
        "confidence": 0.50,
        "last_outcome": "INIT",
    },
    "next_actions": ["collect_novel_observations"],
    "known_failures": [],
}

# Decision values that the kernel understands.
DecisionType = Literal["PROMOTED", "REJECTED", "NO_CHANGE_NEEDED"]


class AutonomyKernel:
    """Planifie et mémorise les prochains objectifs de Sentinel."""

    def __init__(
        self,
        state_filename: str | Path = "sentinel_autonomy_state.json",
        report_filename: str | Path = "sentinel_autonomy_report.json",
        db_filename: str | Path = "sentinel_memory.db",
    ) -> None:
        self.state_filename = Path(state_filename)
        self.report_filename = Path(report_filename)
        self.db_filename = Path(db_filename)
        self._ensure_table()
        self.state = self._load_state()

    def _ensure_table(self) -> None:
        self.db_filename.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS autonomy_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    observation_hash TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    baseline_score REAL NOT NULL,
                    candidate_score REAL NOT NULL,
                    next_actions TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    report TEXT NOT NULL
                )
                """
            )
            # Migrer les bases créées par les versions précédentes sans perdre
            # les événements historiques déjà persistés.
            columns = {row[1] for row in connection.execute("PRAGMA table_info(autonomy_events)")}
            for name in ("baseline_score", "candidate_score"):
                if name not in columns:
                    connection.execute(
                        f"ALTER TABLE autonomy_events ADD COLUMN {name} REAL NOT NULL DEFAULT 0.0"
                    )
            # Activer le mode WAL pour une meilleure durabilité et concurrence.
            connection.execute("PRAGMA journal_mode=WAL;")
            # Créer un index sur cycle_id pour accélérer les recherches ciblées.
            connection.execute("CREATE INDEX IF NOT EXISTS idx_cycle_id ON autonomy_events(cycle_id);")
            # Créer un index sur observation_hash pour accélérer les recherches par hash.
            connection.execute("CREATE INDEX IF NOT EXISTS idx_observation_hash ON autonomy_events(observation_hash);")
            connection.commit()

    def _load_state(self) -> dict[str, Any]:
        if not self.state_filename.exists():
            return deepcopy(DEFAULT_STATE)
        try:
            loaded = json.loads(self.state_filename.read_text(encoding="utf-8"))
            state = deepcopy(DEFAULT_STATE)
            state.update(loaded)
            strategy = deepcopy(DEFAULT_STATE["strategy"])
            strategy.update(loaded.get("strategy", {}))
            state["strategy"] = strategy
            return state
        except (OSError, ValueError, TypeError) as exc:
            # Sauvegarder le fichier corrompu pour analyse future.
            backup_name = self.state_filename.with_name(
                f"{self.state_filename.name}.corrupt.{int(datetime.now().timestamp())}"
            )
            try:
                self.state_filename.rename(backup_name)
            except OSError:
                pass  # Si le renommage échoue, on ignore et continuons.
            return deepcopy(DEFAULT_STATE)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _atomic_write_json(self, path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @staticmethod
    def _actions_for(decision: DecisionType, source_count: int) -> list[str]:
        if decision == "PROMOTED":
            return [
                "reuse_promoted_policy_next_cycle",
                "measure_source_reliability_again",
                "search_for_new_observations",
            ]
        if decision == "REJECTED":
            return [
                "record_rejection_reason",
                "collect_more_evidence_before_retrying",
                "run_regression_checks",
            ]
        if decision == "NO_CHANGE_NEEDED":
            return ["wait_for_novel_observation", "maintain_current_policy"]
        raise ValueError(f"Unsupported decision value: {decision}")

    def _prune_events(self, keep_last: int = 1000) -> None:
        """Supprime les événements les plus anciens en conservant les `keep_last` plus récents."""
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                DELETE FROM autonomy_events
                WHERE id NOT IN (
                    SELECT id FROM autonomy_events ORDER BY id DESC LIMIT ?
                );
                """,
                (keep_last,),
            )
            connection.commit()

    def advance(
        self,
        *,
        cycle_id: str,
        observation_hash: str,
        decision: DecisionType,
        baseline_score: float,
        candidate_score: float,
        source_count: int,
        feedback_report: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Met à jour la stratégie et planifie la prochaine action autonome.

        Args:
            cycle_id: Identifiant unique du cycle.
            observation_hash: Hash de l'observation traitée.
            decision: Décision prise par le moteur (PROMOTED, REJECTED ou NO_CHANGE_NEEDED).
            baseline_score: Score de référence.
            candidate_score: Score du candidat.
            source_count: Nombre de sources d'information.
            feedback_report: Rapport de feedback détaillé.
        """
        if decision not in ("PROMOTED", "REJECTED", "NO_CHANGE_NEEDED"):
            raise ValueError(f"Invalid decision '{decision}'. Expected one of PROMOTED, REJECTED, NO_CHANGE_NEEDED.")

        previous = deepcopy(self.state)
        self.state["cycle_number"] = int(self.state.get("cycle_number", 0)) + 1
        self.state["total_plans"] = int(self.state.get("total_plans", 0)) + 1
        self.state["last_observation_hash"] = observation_hash
        actions = self._actions_for(decision, source_count)
        self.state["next_actions"] = actions

        strategy = dict(self.state.get("strategy", {}))
        confidence = float(strategy.get("confidence", 0.50))
        if decision == "PROMOTED":
            delta = 0.07 if source_count >= 3 else 0.05
            confidence = min(0.95, confidence + delta)
            self.state["successful_experiments"] = int(self.state.get("successful_experiments", 0)) + 1
            strategy["last_outcome"] = "PROMOTED"
        elif decision == "REJECTED":
            delta = 0.02 if source_count >= 3 else 0.03
            confidence = max(0.05, confidence - delta)
            self.state["rejected_experiments"] = int(self.state.get("rejected_experiments", 0)) + 1
            strategy["last_outcome"] = "REJECTED"
        else:
            strategy["last_outcome"] = "NO_CHANGE_NEEDED"
        strategy["confidence"] = round(confidence, 6)
        strategy["last_decision_at"] = self._now()
        self.state["strategy"] = strategy

        event = {
            "cycle_id": cycle_id,
            "created_at": self._now(),
            "observation_hash": observation_hash,
            "decision": decision,
            "baseline_score": baseline_score,
            "candidate_score": candidate_score,
            "next_actions": actions,
            "strategy": strategy,
            "feedback": dict(feedback_report),
        }
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                INSERT INTO autonomy_events
                (cycle_id, created_at, observation_hash, decision, baseline_score, candidate_score, next_actions, strategy, report)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cycle_id,
                    event["created_at"],
                    observation_hash,
                    decision,
                    baseline_score,
                    candidate_score,
                    json.dumps(actions, ensure_ascii=False, sort_keys=True),
                    json.dumps(strategy, ensure_ascii=False, sort_keys=True),
                    json.dumps(event, ensure_ascii=False, sort_keys=True),
                ),
            )
            connection.commit()
        self._prune_events()

        should_persist = True
        if should_persist:
            self._atomic_write_json(self.state_filename, self.state)
            self._atomic_write_json(self.report_filename, event)

        return {
            "cycle_id": cycle_id,
            "autonomy_mode": self.state["autonomy_mode"],
            "decision": decision,
            "next_actions": actions,
            "strategy": strategy,
            "cycle_number": self.state["cycle_number"],
            "should_persist": should_persist,
            "previous_state": previous,
        }

    def get_recent_events(self, limit: int = 10) -> list[dict[str, Any]]:
        """Récupère les `limit` derniers événements sous forme de dictionnaires décodés.

        Cette méthode facilite l'inspection rapide de l'historique sans charger
        toute la table en mémoire.
        """
        with sqlite3.connect(self.db_filename) as connection:
            cursor = connection.execute(
                "SELECT report FROM autonomy_events ORDER BY id DESC LIMIT ?", (limit,)
            )
            rows = cursor.fetchall()
        return [json.loads(row[0]) for row in rows]
