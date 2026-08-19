import json
from datetime import datetime
from typing import Any, Mapping

from loguru import logger

from memory_manager import SentinelMemory


class LearningEngine:
    """Analyse les observations en tenant compte de la politique persistante."""

    def __init__(self):
        self.memory = SentinelMemory()

    def evaluate_threats(
        self,
        collected_data: Mapping[str, Any],
        policy: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Produit un rapport déterministe et réutilise la politique apprise."""
        policy = policy or {}
        reliability = dict(policy.get("source_reliability", {}))
        minimum_sources = int(policy.get("minimum_sources", 1))
        confidence_threshold = float(policy.get("confidence_threshold", 0.65))
        logger.info("🧠 Moteur d'apprentissage activé. Analyse des données en cours...")

        analysis_result: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "status": "analyzed" if len(collected_data) >= minimum_sources else "insufficient_sources",
            "intelligence_score": 85,
            "mutations_suggested": [],
            "policy_version": policy.get("version", 1),
            "confidence_threshold": confidence_threshold,
            "source_reliability": reliability,
        }

        weighted_scores: list[float] = []
        for source, content in collected_data.items():
            source_reliability = float(reliability.get(source, 0.5))
            weighted_scores.append(source_reliability)
            if content and source_reliability >= 0.45:
                analysis_result["mutations_suggested"].append(f"optimize_defense_{source}")
                logger.success(f"🎯 Pattern d'intelligence détecté pour la source : {source}")
            elif source:
                analysis_result["mutations_suggested"].append(f"monitor_source_{source}")
                logger.warning(f"📝 Source à surveiller selon la mémoire : {source}")

        if weighted_scores:
            reliability_score = sum(weighted_scores) / len(weighted_scores)
            analysis_result["intelligence_score"] = round(70 + reliability_score * 30, 2)
        else:
            logger.warning("📝 Aucune nouvelle donnée à analyser. Repos du noyau.")

        # Sauvegarde automatique avant toute décision adaptative.
        self.memory.backup_memory()
        return analysis_result


if __name__ == "__main__":
    engine = LearningEngine()
    print(json.dumps(engine.evaluate_threats({"github": "active"}), indent=2))
