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
            "intelligence_score": 0.0,
            "mutations_suggested": [],
            "policy_version": policy.get("version", 1),
            "confidence_threshold": confidence_threshold,
            "source_reliability": reliability,
            "quality_metrics": {},
            "source_metrics": {},
        }

        weighted_scores: list[float] = []
        content_hashes: set[str] = set()
        quality_values: list[float] = []
        for source, content in collected_data.items():
            text = str(content or "")
            source_reliability = max(0.0, min(1.0, float(reliability.get(source, 0.5))))
            weighted_scores.append(source_reliability)
            content_length = len(text.strip())
            non_empty = bool(text.strip())
            length_quality = min(1.0, content_length / 1000.0)
            content_quality = round((0.45 if non_empty else 0.0) + (0.55 * length_quality), 6)
            content_hash = __import__("hashlib").sha256(text.encode("utf-8")).hexdigest()
            content_hashes.add(content_hash)
            quality_values.append(content_quality)
            analysis_result["source_metrics"][source] = {
                "content_length": content_length,
                "content_quality": content_quality,
                "reliability": round(source_reliability, 6),
                "content_hash": content_hash,
            }
            if non_empty and source_reliability >= 0.45:
                analysis_result["mutations_suggested"].append(f"optimize_defense_{source}")
                logger.success(f"🎯 Pattern d'intelligence détecté pour la source : {source}")
            elif source:
                analysis_result["mutations_suggested"].append(f"monitor_source_{source}")
                logger.warning(f"📝 Source à surveiller selon la mémoire : {source}")

        if weighted_scores:
            reliability_score = sum(weighted_scores) / len(weighted_scores)
            content_quality = sum(quality_values) / len(quality_values)
            source_diversity = len(content_hashes) / len(weighted_scores)
            freshness = 1.0 if any(quality >= 0.55 for quality in quality_values) else 0.25
            coverage = min(1.0, len(weighted_scores) / max(1, minimum_sources * 2))
            analysis_result["quality_metrics"] = {
                "content_quality": round(content_quality, 6),
                "source_diversity": round(source_diversity, 6),
                "freshness": round(freshness, 6),
                "coverage": round(coverage, 6),
            }
            analysis_result["intelligence_score"] = round(
                100 * (
                    reliability_score * 0.45
                    + content_quality * 0.30
                    + source_diversity * 0.15
                    + coverage * 0.10
                ),
                2,
            )
        else:
            logger.warning("📝 Aucune nouvelle donnée à analyser. Repos du noyau.")

        # Sauvegarde automatique avant toute décision adaptative.
        self.memory.backup_memory()
        return analysis_result


if __name__ == "__main__":
    engine = LearningEngine()
    print(json.dumps(engine.evaluate_threats({"github": "active"}), indent=2))
