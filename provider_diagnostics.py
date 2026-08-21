"""Compétence déterministe de diagnostic des fournisseurs Sentinel.

Elle transforme les statuts de transport en actions limitées et vérifiables :
cooldown, fallback, réparation JSON bornée ou inspection de contrat. Aucun secret,
payload ou corps de réponse n'est conservé.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def classify_provider_status(status: str) -> str:
    normalized = str(status or "").upper()
    if normalized.startswith("EMPTY_"):
        return "cooldown_empty_provider_and_fallback"
    if "HTTP_429" in normalized or "PROVIDER_COOLDOWN" in normalized:
        return "respect_cooldown_and_fallback"
    if "INVALID_MODEL_JSON" in normalized:
        return "repair_once_then_cooldown"
    if "HTTP_400" in normalized:
        return "inspect_request_contract_before_retry"
    if "CONNECTION" in normalized or "TIMEOUT" in normalized:
        return "retry_next_provider_with_bounded_attempts"
    if normalized in {"GOOGLE", "CLOUDFLARE", "GROQ", "NVIDIA", "OLLAMA", "REPLICATE"}:
        return "response_received_validate_structure"
    return "record_unknown_provider_state"


def diagnose_provider_attempts(report: Mapping[str, Any]) -> dict[str, Any]:
    attempts = [item for item in report.get("attempts", []) if isinstance(item, Mapping)]
    statuses = [str(item.get("provider", "UNKNOWN")) for item in attempts]
    actions = [classify_provider_status(status) for status in statuses]
    failed = [status for status in statuses if classify_provider_status(status) != "response_received_validate_structure"]
    fallback_observed = len(statuses) >= 2 and len(set(statuses)) >= 2 and bool(failed)
    return {
        "attempt_count": len(attempts),
        "provider_sequence": statuses,
        "recommended_actions": actions,
        "fallback_observed": fallback_observed,
        "diagnostic_score": round((1.0 if actions else 0.0) * (1.0 if fallback_observed or len(statuses) <= 1 else 0.8), 6),
    }


def run_provider_diagnostic(report: Mapping[str, Any]) -> dict[str, Any]:
    """Évalue la compétence sur des variantes distinctes du cycle courant."""
    observed = diagnose_provider_attempts(report)
    variants: Sequence[dict[str, Any]] = (
        {
            "name": "empty_response_variant",
            "score": 1.0 if classify_provider_status("EMPTY_CLOUDFLARE_RESPONSE") == "cooldown_empty_provider_and_fallback" else 0.0,
        },
        {
            "name": "rate_limit_variant",
            "score": 1.0 if classify_provider_status("PROVIDER_ERROR:HTTP_429") == "respect_cooldown_and_fallback" else 0.0,
        },
        {
            "name": "invalid_json_variant",
            "score": 1.0 if classify_provider_status("INVALID_MODEL_JSON") == "repair_once_then_cooldown" else 0.0,
        },
    )
    transfer_score = round(sum(item["score"] for item in variants) / len(variants), 6)
    return {
        "skill_name": "provider_failure_diagnosis",
        "observed_diagnostic": observed,
        "transfer_variants": list(variants),
        "transfer_score": transfer_score,
        "transfer_verified": transfer_score >= 0.65,
        "procedure": "Classifier les erreurs fournisseur, appliquer une action bornée et poursuivre uniquement avec un fallback disponible.",
    }


__all__ = ["classify_provider_status", "diagnose_provider_attempts", "run_provider_diagnostic"]
