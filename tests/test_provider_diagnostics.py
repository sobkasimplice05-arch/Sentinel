from provider_diagnostics import diagnose_provider_attempts, run_provider_diagnostic


def test_provider_diagnostic_classifies_empty_response_and_fallback():
    report = {
        "attempts": [
            {"provider": "EMPTY_CLOUDFLARE_RESPONSE"},
            {"provider": "GOOGLE"},
        ]
    }

    diagnosis = diagnose_provider_attempts(report)

    assert diagnosis["fallback_observed"] is True
    assert diagnosis["recommended_actions"][0] == "cooldown_empty_provider_and_fallback"


def test_provider_diagnostic_has_three_verified_transfer_variants():
    report = run_provider_diagnostic({"attempts": [{"provider": "PROVIDER_ERROR:HTTP_429"}]})

    assert report["transfer_verified"] is True
    assert report["transfer_score"] == 1.0
    assert len(report["transfer_variants"]) == 3
