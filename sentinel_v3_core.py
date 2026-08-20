#!/usr/bin/env python3
import subprocess
from datetime import datetime, timezone
from typing import Any

from loguru import logger

from agent_general_kernel import GeneralAgentKernel
from ai_matrix import AIMatrix
from autonomy_kernel import AutonomyKernel
from data_collector import DataCollector
from evolution_guard import EvolutionGuard
from feedback_learning import AdaptiveFeedback
from learning_engine import LearningEngine
from memory_manager import SentinelMemory
from notifier import SentinelNotifier
from self_modification import SelfModificationEngine
from sentinel_janitor import SentinelJanitor


class SentinelV3Core:
    """Cycle v3 : observer, mémoire, feedback et persistance contrôlée."""

    def __init__(self):
        logger.info("🌐 Centralisation du Noyau Distribué Sentinel v3.1...")
        self.collector = DataCollector()
        self.engine = LearningEngine()
        self.memory = SentinelMemory()
        self.feedback = AdaptiveFeedback()
        self.autonomy = AutonomyKernel()
        self.agent_general = GeneralAgentKernel()
        self.self_modifier = SelfModificationEngine()
        self.notifier = SentinelNotifier()
        self.ai = AIMatrix()
        self.guard = EvolutionGuard()
        self.janitor = SentinelJanitor()

    def commit_memory(self, include_self_modification_report: bool = False) -> bool:
        """Persiste les preuves et les patches approuvés; aucun force-push."""
        tracked_files = [
            "sentinel_memory.db",
            "src/core/circular_memory.json",
            "sentinel_real_web_discoveries.json",
            "sentinel_learning_state.json",
            "feedback_report.json",
            "sentinel_autonomy_state.json",
            "sentinel_autonomy_report.json",
            "agent_general_state.json",
            "agent_general_report.json",
            "self_modification_provider_cooldown.json",
        ]
        if include_self_modification_report:
            tracked_files.extend(
                [
                    "self_modification_report.json",
                    "learning_engine.py",
                    "feedback_learning.py",
                    "autonomy_kernel.py",
                ]
            )
        try:
            subprocess.run(
                ["git", "config", "user.email", "sentinel-v3@evolution.ai"],
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Sentinel-V3-Core"],
                check=True,
            )
            subprocess.run(["git", "add", *tracked_files], check=True)
            if subprocess.run(["git", "diff", "--cached", "--quiet"], check=False).returncode == 0:
                logger.info("ℹ️ Aucun nouvel artefact à promouvoir; pas de commit artificiel.")
                return True

            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            subprocess.run(
                ["git", "commit", "-m", f"🧬 FEEDBACK: cycle adaptatif vérifié {timestamp}"],
                check=True,
            )
            subprocess.run(["git", "push", "origin", "main"], check=True)
            logger.info("✅ Preuves du cycle poussées sur main sans écrasement d'historique.")
            return True
        except subprocess.CalledProcessError as exc:
            logger.error(f"❌ Persistance Git échouée: {exc}")
            return False

    def run_cycle(self) -> bool:
        logger.info("⚡ Début du cycle d'apprentissage et de feedback...")
        try:
            self.janitor.purge_old_backups()
            raw_data = self.collector.fetch_all()
            active_sources = ", ".join(raw_data.keys()) if raw_data else "Aucune"

            # La décision API reste volontairement compatible avec la configuration actuelle.
            # Elle ne devient pas une mutation tant qu'aucun patch n'est généré et mesuré.
            preliminary_report: dict[str, Any] = self.engine.evaluate_threats(raw_data, self.feedback.policy)
            ai_decision = self.ai.consult_brain(preliminary_report)
            preliminary_report["intelligence_score"] = ai_decision.get("confidence", 0)
            preliminary_report["ai_source"] = ai_decision.get("source", "unknown")
            preliminary_report["decision_status"] = ai_decision.get("decision", "unknown")

            feedback_report = self.feedback.run_cycle(raw_data, preliminary_report, ai_decision)
            feedback_decision = feedback_report["decision"]
            preliminary_report["feedback_decision"] = feedback_decision
            preliminary_report["feedback_cycle_id"] = feedback_report["cycle_id"]
            preliminary_report["observation_hash"] = feedback_report["observation_hash"]
            preliminary_report["baseline_score"] = feedback_report["baseline_score"]
            preliminary_report["candidate_score"] = feedback_report["candidate_score"]

            autonomy_report = self.autonomy.advance(
                cycle_id=feedback_report["cycle_id"],
                observation_hash=feedback_report["observation_hash"],
                decision=feedback_decision,
                baseline_score=feedback_report["baseline_score"],
                candidate_score=feedback_report["candidate_score"],
                source_count=len(raw_data),
                feedback_report=feedback_report,
            )
            preliminary_report["autonomy_mode"] = autonomy_report["autonomy_mode"]
            preliminary_report["autonomy_cycle_number"] = autonomy_report["cycle_number"]
            preliminary_report["next_actions"] = autonomy_report["next_actions"]
            preliminary_report["strategy"] = autonomy_report["strategy"]

            objective = self.agent_general.select_objective(raw_data.keys())
            capabilities = list(self.autonomy.state.get("capabilities", []))
            capabilities.append("source_modification")
            agent_plan = self.agent_general.build_plan(objective, capabilities)

            self_modification_report = self.self_modifier.run_cycle(
                feedback=feedback_report,
                autonomy=autonomy_report,
            )
            preliminary_report["self_modification"] = self_modification_report
            self_modification_decision = self_modification_report["decision"]

            agent_general_report = self.agent_general.record_cycle(
                objective=objective,
                plan=agent_plan,
                observation_hash=feedback_report["observation_hash"],
                feedback=feedback_report,
                self_modification=self_modification_report,
            )
            preliminary_report["agent_general"] = agent_general_report

            if feedback_decision != "NO_CHANGE_NEEDED":
                self.memory.save_learning(
                    mutation_id=feedback_decision,
                    success=feedback_decision == "PROMOTED",
                    learnings_dict=preliminary_report,
                )
                persisted = self.commit_memory(
                    include_self_modification_report=self_modification_decision in {"PROMOTED", "REJECTED"}
                )
                if not persisted:
                    return False
            elif autonomy_report["should_persist"]:
                # Heartbeat stratégique périodique : la mémoire longue durée
                # est conservée sans fabriquer un faux succès de mutation.
                persisted = self.commit_memory(
                    include_self_modification_report=self_modification_decision in {"PROMOTED", "REJECTED"}
                )
                if not persisted:
                    return False
            elif self_modification_decision in {"PROMOTED", "REJECTED"}:
                persisted = self.commit_memory(include_self_modification_report=True)
                if not persisted:
                    return False
            else:
                logger.info("ℹ️ Observation déjà connue: aucun faux apprentissage ni commit généré.")

            logger.info(
                f"✅ Cycle: sources={active_sources}; décision={feedback_decision}; "
                f"baseline={feedback_report['baseline_score']}; "
                f"candidat={feedback_report['candidate_score']}; "
                f"prochaines_actions={autonomy_report['next_actions']}; "
                f"auto_code={self_modification_decision}; "
                f"objectif={objective['title']}"
            )
            return True
        except Exception as exc:
            logger.exception(f"❌ CYCLE FAILED: {exc}")
            return False


if __name__ == "__main__":
    sentinel = SentinelV3Core()
    raise SystemExit(0 if sentinel.run_cycle() else 1)
