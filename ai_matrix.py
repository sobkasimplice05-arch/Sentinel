"""Décision stratégique structurée pour le cycle Sentinel V3.

La matrice ne promeut jamais de code. Elle produit uniquement une recommandation
JSON traçable; la promotion reste confiée au moteur d'auto-modification isolé.
"""
from __future__ import annotations

import json
from typing import Any, Mapping

from loguru import logger

from self_modification import SelfModificationEngine


class AIMatrix:
    """Interroge le routeur V3 et refuse les validations non vérifiables."""

    def __init__(self) -> None:
        self.provider_engine = SelfModificationEngine()

    @staticmethod
    def _decode_json(raw: str) -> dict[str, Any] | None:
        text = str(raw).strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].lstrip()
        try:
            payload = json.loads(text)
        except (TypeError, ValueError):
            start, end = text.find("{"), text.rfind("}")
            if start < 0 or end <= start:
                return None
            try:
                payload = json.loads(text[start : end + 1])
            except (TypeError, ValueError):
                return None
        return payload if isinstance(payload, dict) else None

    @staticmethod
    def _confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.0
        if 0.0 <= confidence <= 1.0:
            confidence *= 100.0
        return round(max(0.0, min(100.0, confidence)), 2)

    @staticmethod
    def _unavailable(provider: str, report: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "decision": provider if provider.startswith(("MODEL_", "PROVIDER_", "INVALID_")) else "MODEL_UNAVAILABLE",
            "confidence": 0.0,
            "source": provider,
            "hypothesis": "Aucune recommandation IA exploitable pour ce cycle.",
            "risks": ["absence de sortie structurée"],
            "evidence": {"input_keys": sorted(str(key) for key in report)},
        }

    def consult_brain(self, security_data: Mapping[str, Any]) -> dict[str, Any]:
        logger.info("🧠 Consultation structurée de la matrice IA Sentinel...")
        prompt = (
            "Analyse le rapport suivant sans modifier de fichier. Retourne uniquement un objet JSON "
            "avec les champs decision, confidence (0 à 100), hypothesis, risks (liste) et evidence. "
            "decision doit être l'une de MODEL_RECOMMENDATION, NO_CHANGE_NEEDED ou RISK_REVIEW.\n\n"
            f"RAPPORT:\n{json.dumps(dict(security_data), ensure_ascii=False, sort_keys=True)[:12000]}"
        )
        raw, provider = self.provider_engine._call_provider(prompt, output_tokens=1024)
        if raw is None:
            logger.warning(f"⚠️ Matrice IA indisponible: {provider}")
            return self._unavailable(provider, security_data)

        payload = self._decode_json(raw)
        if payload is None:
            logger.warning(f"⚠️ Réponse non structurée du fournisseur {provider}; décision refusée.")
            return self._unavailable("INVALID_MODEL_JSON", security_data)

        decision = str(payload.get("decision", "MODEL_RECOMMENDATION")).strip() or "MODEL_RECOMMENDATION"
        if decision not in {"MODEL_RECOMMENDATION", "NO_CHANGE_NEEDED", "RISK_REVIEW"}:
            decision = "RISK_REVIEW"
        risks = payload.get("risks", [])
        if not isinstance(risks, list):
            risks = [str(risks)]
        evidence = payload.get("evidence", {})
        if not isinstance(evidence, (dict, list, str, int, float, bool)):
            evidence = {"raw_type": type(evidence).__name__}
        result = {
            "decision": decision,
            "confidence": self._confidence(payload.get("confidence", 0)),
            "source": provider,
            "hypothesis": str(payload.get("hypothesis", ""))[:2000],
            "risks": [str(item)[:500] for item in risks[:10]],
            "evidence": evidence,
        }
        logger.success(f"🤖 Décision structurée reçue depuis {provider}: {decision}")
        return result


if __name__ == "__main__":
    print(json.dumps(AIMatrix().consult_brain({"status": "test"}), ensure_ascii=False, indent=2))


__all__ = ["AIMatrix"]
