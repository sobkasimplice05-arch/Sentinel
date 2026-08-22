"""Point d'entrée minimal pour l'analyse cybersécurité de Sentinel.

Le dépôt ne contenait pas d'implémentation exploitable pour ce module. Cette
version ne réalise aucune action réseau, aucune exécution de commande et aucune
modification automatique ; elle fournit seulement un contrat explicite pour les
intégrations futures.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class SecurityAssessment:
    """Résultat prudent lorsqu'aucune analyse spécialisée n'est disponible."""

    status: str
    risk: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "risk": self.risk,
            "reason": self.reason,
        }


class CybersecurityEngine:
    """Expose une analyse passive et non destructive par défaut."""

    def assess(self, evidence: Mapping[str, Any] | None = None) -> dict[str, str]:
        """Retourne un état prudent sans inventer de verdict de sécurité."""
        del evidence
        return SecurityAssessment(
            status="not_implemented",
            risk="unknown",
            reason="Aucun analyseur cybersécurité spécialisé n'est configuré.",
        ).as_dict()


__all__ = ["CybersecurityEngine", "SecurityAssessment"]
