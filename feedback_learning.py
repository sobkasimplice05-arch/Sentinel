#!/usr/bin/env python3
"""Boucle d'apprentissage et de feedback contrôlée pour Sentinel v3.

Le moteur adapte une politique persistante et vérifiable; il ne réécrit pas
arbitrairement le code Python. Une adaptation n'est promue que si elle est
valide, mesurable et fondée sur une observation nouvelle.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


DEFAULT_POLICY: dict[str, Any] = {
    "version": 1,
    "confidence_threshold": 0.65,
    "minimum_sources": 1,
    "source_reliability": {},
    "observation_history": [],
}

DEFAULT_STATE: dict[str, Any] = {
    "version": 1,
    "last_observation_hash": None,
    "last_cycle_id": None,
    "total_cycles": 0,
    "successful_adaptations": 0,
    "rejected_adaptations": 0,
    "policy": DEFAULT_POLICY,
}


class AdaptiveFeedback:
    """Gère la mémoire et l'évolution contrôlée de la politique Sentinel."""

    def __init__(
        self,
        db_filename: str | Path = "sentinel_memory.db",
        state_filename: str | Path = "sentinel_learning_state.json",
        report_filename: str | Path = "feedback_report.json",
    ) -> None:
        self.db_filename = Path(db_filename)
        self.state_filename = Path(state_filename)
        self.report_filename = Path(report_filename)
        self._ensure_table()
        self.state = self._load_state()

    def _ensure_table(self) -> None:
        self.db_filename.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    observation_hash TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    baseline_score REAL,
                    candidate_score REAL,
                    hypothesis TEXT,
                    details TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def _load_state(self) -> dict[str, Any]:
        if not self.state_filename.exists():
            return deepcopy(DEFAULT_STATE)
        try:
            loaded = json.loads(self.state_filename.read_text(encoding="utf-8"))
            state = deepcopy(DEFAULT_STATE)
            state.update({k: v for k, v in loaded.items() if k != "policy"})
            policy = deepcopy(DEFAULT_POLICY)
            policy.update(loaded.get("policy", {}))
            policy["source_reliability"] = dict(policy.get("source_reliability", {}))
            policy["observation_history"] = list(policy.get("observation_history", []))[-200:]
            policy["confidence_threshold"] = round(
                max(0.50, min(0.90, float(policy.get("confidence_threshold", 0.65)))),
                6,
            )
            state["policy"] = policy
            return state
        except (OSError, ValueError, TypeError):
            return deepcopy(DEFAULT_STATE)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _hash_payload(payload: Mapping[str, Any]) -> str:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def build_observation(
        self,
        collected_data: Mapping[str, Any],
        intelligence_report: Mapping[str, Any],
        ai_decision: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Construit une observation reproductible et non sensible."""
        sources: dict[str, Any] = {}
        for source in sorted(collected_data):
            content = str(collected_data[source])
            sources[source] = {
                "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "content_length": len(content),
                "non_empty": bool(content.strip()),
            }
        payload = {
            "sources": sources,
            "suggestions": intelligence_report.get("mutations_suggested", []),
            "ai_source": ai_decision.get("source", "unknown"),
            "ai_decision": ai_decision.get("decision", "unknown"),
            "ai_confidence": float(ai_decision.get("confidence", 0.0) or 0.0),
            "quality_metrics": intelligence_report.get("quality_metrics", {}),
        }
        observation_hash = self._hash_payload(payload)
        history = set(self.state.get("policy", {}).get("observation_history", []))
        return {
            "observation_hash": observation_hash,
            "sources": sources,
            "source_count": len(sources),
            "novelty_score": 0.0 if observation_hash in history else 1.0,
            "quality_metrics": dict(payload.get("quality_metrics", {})),
            "payload": payload,
        }

    @staticmethod
    def _policy_score(policy: Mapping[str, Any], observation: Mapping[str, Any]) -> float:
        sources = observation.get("sources", {})
        if not sources:
            return 0.0
        reliability = policy.get("source_reliability", {})
        values = [float(reliability.get(name, 0.5)) for name in sources]
        coverage = min(1.0, len(sources) / 2.0)
        metrics = observation.get("quality_metrics", {})
        quality_values = [
            float(metrics.get(name, 0.5))
            for name in ("content_quality", "source_diversity", "freshness")
        ]
        quality_score = sum(max(0.0, min(1.0, value)) for value in quality_values) / len(quality_values)
        novelty = max(0.0, min(1.0, float(observation.get("novelty_score", 1.0))))
        stability_penalty = abs(float(policy.get("confidence_threshold", 0.65)) - 0.65) * 0.1
        reliability_score = sum(values) / len(values)
        return round(reliability_score * 0.55 + coverage * 0.15 + quality_score * 0.20 + novelty * 0.10 - stability_penalty, 6)

    @staticmethod
    def _propose_policy(
        current: Mapping[str, Any], observation: Mapping[str, Any]
    ) -> tuple[dict[str, Any], str]:
        candidate = deepcopy(dict(current))
        reliability = dict(candidate.get("source_reliability", {}))
        for source, metadata in observation.get("sources", {}).items():
            measured_quality = 0.9 if metadata.get("non_empty") and metadata.get("content_length", 0) >= 64 else 0.2
            previous = float(reliability.get(source, 0.5))
            reliability[source] = round(previous * 0.8 + measured_quality * 0.2, 6)

        source_count = int(observation.get("source_count", 0))
        threshold = float(candidate.get("confidence_threshold", 0.65))
        if source_count >= 2:
            threshold -= 0.01
        elif source_count == 0:
            threshold += 0.01
        candidate["confidence_threshold"] = round(max(0.50, min(0.90, threshold)), 6)
        candidate["source_reliability"] = reliability
        history = list(candidate.get("observation_history", []))
        history.append(str(observation.get("observation_hash", "")))
        candidate["observation_history"] = [item for item in history if item][-200:]
        candidate["version"] = int(candidate.get("version", 1)) + 1
        hypothesis = (
            "Ajuster la fiabilité des sources selon la fraîcheur observée et "
            "adapter le seuil selon la couverture des sources."
        )
        return candidate, hypothesis

    @staticmethod
    def _validate_policy(policy: Mapping[str, Any]) -> tuple[bool, str]:
        threshold = float(policy.get("confidence_threshold", -1))
        if not 0.50 <= threshold <= 0.90:
            return False, "confidence_threshold hors limites [0.50, 0.90]"
        minimum_sources = int(policy.get("minimum_sources", 0))
        if not 1 <= minimum_sources <= 10:
            return False, "minimum_sources hors limites [1, 10]"
        for source, value in dict(policy.get("source_reliability", {})).items():
            if not isinstance(source, str) or not 0.0 <= float(value) <= 1.0:
                return False, f"fiabilité invalide pour {source}"
        history = policy.get("observation_history", [])
        if not isinstance(history, list) or len(history) > 200 or any(not isinstance(item, str) or not item for item in history):
            return False, "observation_history invalide"
        return True, "policy_valid"

    def _record_event(
        self,
        *,
        cycle_id: str,
        observation_hash: str,
        decision: str,
        baseline_score: float,
        candidate_score: float,
        hypothesis: str,
        details: Mapping[str, Any],
    ) -> None:
        with sqlite3.connect(self.db_filename) as connection:
            connection.execute(
                """
                INSERT INTO feedback_events
                (cycle_id, created_at, observation_hash, decision, baseline_score,
                 candidate_score, hypothesis, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cycle_id,
                    self._now(),
                    observation_hash,
                    decision,
                    baseline_score,
                    candidate_score,
                    hypothesis,
                    json.dumps(details, ensure_ascii=False, sort_keys=True),
                ),
            )
            connection.commit()

    def run_cycle(
        self,
        collected_data: Mapping[str, Any],
        intelligence_report: Mapping[str, Any],
        ai_decision: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Exécute une adaptation déterministe avec déduplication et garde-fous."""
        observation = self.build_observation(collected_data, intelligence_report, ai_decision)
        observation_hash = observation["observation_hash"]
        cycle_id = f"cycle-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{observation_hash[:12]}"
        current_policy = deepcopy(self.state["policy"])

        if observation_hash == self.state.get("last_observation_hash"):
            score = self._policy_score(current_policy, observation)
            report = {
                "cycle_id": cycle_id,
                "created_at": self._now(),
                "decision": "NO_CHANGE_NEEDED",
                "changed": False,
                "observation_hash": observation_hash,
                "baseline_score": score,
                "candidate_score": score,
                "reason": "observation déjà traitée; aucune nouvelle preuve",
                "policy_before": current_policy,
                "policy_after": current_policy,
            }
            self.report_filename.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return {**report, "policy": current_policy}

        candidate_policy, hypothesis = self._propose_policy(current_policy, observation)
        valid, validation_reason = self._validate_policy(candidate_policy)
        baseline_score = self._policy_score(current_policy, observation)
        candidate_score = self._policy_score(candidate_policy, observation)
        changed = candidate_policy != current_policy
        decision = "PROMOTED" if valid and changed and candidate_score >= baseline_score else "REJECTED"
        reason = "adaptation validée par la baseline" if decision == "PROMOTED" else validation_reason
        if decision == "REJECTED" and valid:
            reason = "score candidat inférieur à la baseline ou aucun changement"

        self.state["total_cycles"] = int(self.state.get("total_cycles", 0)) + 1
        self.state["last_observation_hash"] = observation_hash
        self.state["last_cycle_id"] = cycle_id
        if decision == "PROMOTED":
            self.state["policy"] = candidate_policy
            self.state["successful_adaptations"] = int(self.state.get("successful_adaptations", 0)) + 1
        else:
            self.state["rejected_adaptations"] = int(self.state.get("rejected_adaptations", 0)) + 1

        details = {
            "observation": observation,
            "policy_before": current_policy,
            "policy_after": self.state["policy"],
            "validation": validation_reason,
            "reason": reason,
        }
        self._record_event(
            cycle_id=cycle_id,
            observation_hash=observation_hash,
            decision=decision,
            baseline_score=baseline_score,
            candidate_score=candidate_score,
            hypothesis=hypothesis,
            details=details,
        )
        self.state_filename.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report = {
            "cycle_id": cycle_id,
            "created_at": self._now(),
            "decision": decision,
            "changed": decision == "PROMOTED",
            "observation_hash": observation_hash,
            "baseline_score": baseline_score,
            "candidate_score": candidate_score,
            "hypothesis": hypothesis,
            "reason": reason,
            "policy_before": current_policy,
            "policy_after": self.state["policy"],
        }
        self.report_filename.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {**report, "policy": self.state["policy"]}

    @property
    def policy(self) -> dict[str, Any]:
        return deepcopy(self.state["policy"])
