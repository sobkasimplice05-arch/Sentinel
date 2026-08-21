#!/usr/bin/env python3
"""Noyau expérimental d'agent général pour Sentinel.

Ce module ne prétend pas être une AGI. Il fournit les primitives qui manquent à
un simple worker : objectifs persistants, plans multi-étapes, registre de
compétences, épisodes et évaluation du transfert vers des tâches nouvelles.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


DEFAULT_STATE: dict[str, Any] = {
    "version": 1,
    "mode": "EXPERIMENTAL_GENERAL_AGENT",
    "cycle_number": 0,
    "current_objective_id": None,
    "current_objective": None,
    "active_plan": [],
    "capability_profile": {
        "observation": 0.0,
        "memory": 0.0,
        "planning": 0.0,
        "tool_use": 0.0,
        "source_modification": 0.0,
        "transfer": 0.0,
    },
    "transfer_verified": False,
    "last_outcome": "INIT",
}


class GeneralAgentKernel:
    """Orchestrateur persistant d’objectifs et de compétences expérimentales."""

    def __init__(
        self,
        state_filename: str | Path = "agent_general_state.json",
        report_filename: str | Path = "agent_general_report.json",
        db_filename: str | Path = "sentinel_memory.db",
    ) -> None:
        self.state_filename = Path(state_filename)
        self.report_filename = Path(report_filename)
        self.db_filename = Path(db_filename)
        self._ensure_tables()
        self.state = self._load_state()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _hash(payload: Mapping[str, Any]) -> str:
        encoded = json.dumps(dict(payload), sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]

    def _ensure_tables(self) -> None:
        self.db_filename.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_filename) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS agent_objectives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    title TEXT NOT NULL,
                    context TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    outcome TEXT
                );
                CREATE TABLE IF NOT EXISTS agent_skills (
                    name TEXT PRIMARY KEY,
                    version INTEGER NOT NULL,
                    procedure TEXT NOT NULL,
                    competence_score REAL NOT NULL,
                    transfer_score REAL,
                    successes INTEGER NOT NULL,
                    failures INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agent_episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    objective_id INTEGER,
                    observation_hash TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    action TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    score REAL NOT NULL,
                    transfer_status TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agent_transfer_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    skill_name TEXT NOT NULL,
                    task_variant TEXT NOT NULL,
                    score REAL NOT NULL,
                    baseline REAL NOT NULL,
                    decision TEXT NOT NULL
                );
                """
            )
            connection.commit()

    def _load_state(self) -> dict[str, Any]:
        if not self.state_filename.exists():
            return deepcopy(DEFAULT_STATE)
        try:
            loaded = json.loads(self.state_filename.read_text(encoding="utf-8"))
            state = deepcopy(DEFAULT_STATE)
            state.update(loaded)
            profile = deepcopy(DEFAULT_STATE["capability_profile"])
            profile.update(loaded.get("capability_profile", {}))
            state["capability_profile"] = profile
            return state
        except (OSError, ValueError, TypeError):
            return deepcopy(DEFAULT_STATE)

    def _persist(self, report: Mapping[str, Any]) -> None:
        self.state_filename.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.report_filename.write_text(json.dumps(dict(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def ensure_objective(self, title: str, context: str = "", priority: int = 50) -> dict[str, Any]:
        title = title.strip()[:500] or "improve_general_agent_capabilities"
        with sqlite3.connect(self.db_filename) as connection:
            row = connection.execute(
                "SELECT id, title, context, priority, status FROM agent_objectives WHERE title = ? AND status = 'PENDING' ORDER BY id DESC LIMIT 1",
                (title,),
            ).fetchone()
            if row:
                objective_id, saved_title, saved_context, saved_priority, status = row
            else:
                cursor = connection.execute(
                    "INSERT INTO agent_objectives(created_at, title, context, priority, status) VALUES (?, ?, ?, ?, 'PENDING')",
                    (self._now(), title, context[:4000], max(1, min(100, int(priority)))),
                )
                objective_id = cursor.lastrowid
                saved_title, saved_context, saved_priority, status = title, context[:4000], priority, "PENDING"
            connection.commit()
        objective = {
            "id": objective_id,
            "title": saved_title,
            "context": saved_context,
            "priority": saved_priority,
            "status": status,
        }
        self.state["current_objective_id"] = objective_id
        self.state["current_objective"] = objective
        return objective

    def select_objective(self, observation_keys: Sequence[str] = ()) -> dict[str, Any]:
        with sqlite3.connect(self.db_filename) as connection:
            row = connection.execute(
                "SELECT id, title, context, priority, status FROM agent_objectives WHERE status = 'PENDING' ORDER BY priority DESC, id ASC LIMIT 1"
            ).fetchone()
        if row:
            objective = {"id": row[0], "title": row[1], "context": row[2], "priority": row[3], "status": row[4]}
            self.state["current_objective_id"] = objective["id"]
            self.state["current_objective"] = objective
            return objective
        return self.ensure_objective(
            "improve_observation_and_transfer",
            f"Sources observées: {', '.join(observation_keys) or 'aucune'}; chercher une compétence mesurable et transférable.",
            60,
        )

    def build_plan(self, objective: Mapping[str, Any], capabilities: Sequence[str] = ()) -> list[dict[str, Any]]:
        available = set(capabilities)
        plan = [
            {"step": 1, "name": "frame_objective", "action": "formalize_success_criteria", "status": "READY"},
            {"step": 2, "name": "retrieve_memory", "action": "retrieve_relevant_episodes_and_skills", "status": "READY"},
            {"step": 3, "name": "act_and_experiment", "action": "execute_tools_or_candidate_patch_in_isolation", "status": "READY"},
            {"step": 4, "name": "evaluate_transfer", "action": "test_on_unseen_task_variant", "status": "READY"},
            {"step": 5, "name": "consolidate", "action": "promote_skill_or_record_failure", "status": "READY"},
        ]
        if "source_modification" not in available:
            plan[2]["action"] = "execute_observation_and_safe_candidate_experiment"
        self.state["active_plan"] = plan
        return plan

    def register_skill(
        self,
        name: str,
        procedure: str,
        score: float,
        transfer_scores: Sequence[float] = (),
        success: bool = True,
    ) -> dict[str, Any]:
        transfer_score = round(sum(transfer_scores) / len(transfer_scores), 6) if transfer_scores else None
        status = "CANDIDATE" if transfer_score is None else ("PROMOTED" if transfer_score >= 0.65 and score >= 0.65 else "REJECTED")
        with sqlite3.connect(self.db_filename) as connection:
            old = connection.execute("SELECT version, successes, failures FROM agent_skills WHERE name = ?", (name,)).fetchone()
            version = (old[0] + 1) if old else 1
            successes = (old[1] if old else 0) + int(success)
            failures = (old[2] if old else 0) + int(not success)
            connection.execute(
                """INSERT INTO agent_skills(name, version, procedure, competence_score, transfer_score, successes, failures, status, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET version=excluded.version, procedure=excluded.procedure,
                   competence_score=excluded.competence_score, transfer_score=excluded.transfer_score,
                   successes=excluded.successes, failures=excluded.failures, status=excluded.status, updated_at=excluded.updated_at""",
                (name, version, procedure[:8000], score, transfer_score, successes, failures, status, self._now()),
            )
            connection.commit()
        if status == "PROMOTED":
            self.state["capability_profile"]["transfer"] = max(self.state["capability_profile"]["transfer"], transfer_score or 0.0)
            self.state["transfer_verified"] = True
        return {"name": name, "version": version, "status": status, "competence_score": score, "transfer_score": transfer_score}

    def get_skill(self, name: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_filename) as connection:
            row = connection.execute(
                "SELECT name, version, competence_score, transfer_score, successes, failures, status, updated_at FROM agent_skills WHERE name = ?",
                (name,),
            ).fetchone()
        if not row:
            return None
        return {
            "name": row[0], "version": row[1], "competence_score": row[2], "transfer_score": row[3],
            "successes": row[4], "failures": row[5], "status": row[6], "updated_at": row[7],
        }

    def record_cycle(
        self,
        *,
        objective: Mapping[str, Any],
        plan: Sequence[Mapping[str, Any]],
        observation_hash: str,
        feedback: Mapping[str, Any],
        self_modification: Mapping[str, Any],
        skill_learning: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.state["cycle_number"] = int(self.state.get("cycle_number", 0)) + 1
        feedback_decision = str(feedback.get("decision", "UNKNOWN"))
        score = float(feedback.get("candidate_score", 0.0))
        action = str(self_modification.get("decision", "NO_SOURCE_PATCH"))
        learning = dict(skill_learning or {})
        transfer_status = str(learning.get("transfer_status", "NOT_MEASURED"))
        episode = {
            "created_at": self._now(),
            "objective_id": objective.get("id"),
            "observation_hash": observation_hash,
            "plan": list(plan),
            "action": action,
            "outcome": feedback_decision,
            "score": score,
            "transfer_status": transfer_status,
        }
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """INSERT INTO agent_episodes(created_at, objective_id, observation_hash, plan, action, outcome, score, transfer_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    episode["created_at"],
                    episode["objective_id"],
                    observation_hash,
                    json.dumps(list(plan), ensure_ascii=False),
                    action,
                    feedback_decision,
                    score,
                    transfer_status,
                ),
            )
            connection.commit()
        self.state["last_outcome"] = feedback_decision
        report = {
            "mode": self.state["mode"],
            "cycle_number": self.state["cycle_number"],
            "objective": dict(objective),
            "plan": list(plan),
            "episode": episode,
            "skill_learning": {
                "status": learning.get("status", "OBSERVATION_SKILL_UPDATED"),
                "transfer_status": transfer_status,
                "note": learning.get("note", "Une compétence générale n'est promue qu'après un test sur une variante non vue."),
                "skill": learning.get("skill"),
                "diagnostic": learning.get("diagnostic"),
            },
            "capability_profile": self.state["capability_profile"],
            "transfer_verified": self.state["transfer_verified"],
        }
        self._persist(report)
        return report

    def evaluate_transfer(self, skill_name: str, variants: Sequence[Mapping[str, Any]], baseline: float = 0.5) -> dict[str, Any]:
        scores = [float(variant.get("score", 0.0)) for variant in variants]
        transfer_score = round(sum(scores) / len(scores), 6) if scores else 0.0
        decision = "PROMOTED" if scores and transfer_score > baseline and transfer_score >= 0.65 else "REJECTED"
        for variant, score in zip(variants, scores):
            with sqlite3.connect(self.db_filename) as connection:
                connection.execute(
                    "INSERT INTO agent_transfer_tests(created_at, skill_name, task_variant, score, baseline, decision) VALUES (?, ?, ?, ?, ?, ?)",
                    (self._now(), skill_name, str(variant.get("name", "unknown")), score, baseline, decision),
                )
                connection.commit()
        skill = self.register_skill(skill_name, "transfer_evaluated", transfer_score, scores, decision == "PROMOTED")
        return {"skill": skill, "variants": list(variants), "baseline": baseline, "transfer_score": transfer_score, "decision": decision}
