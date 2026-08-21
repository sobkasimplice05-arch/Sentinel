from pathlib import Path

from source_evolution_curriculum import run_source_evolution_curriculum


def _provider_source() -> str:
    return '''def classify_provider_status(status: str) -> str:
    normalized = str(status or "").upper()
    if normalized.startswith("EMPTY_"):
        return "cooldown_empty_provider_and_fallback"
    if "INVALID_MODEL_JSON" in normalized:
        return "repair_once_then_cooldown"
    return "record_unknown_provider_state"
'''


def test_curriculum_promotes_compact_413_recovery_after_transfer(tmp_path):
    Path(tmp_path / "provider_diagnostics.py").write_text(_provider_source(), encoding="utf-8")

    report = run_source_evolution_curriculum(tmp_path)

    assert report["decision"] == "PROMOTED"
    assert report["baseline_score"] == 0.0
    assert report["candidate_score"] == 1.0
    assert report["changed_files"] == ["provider_diagnostics.py"]
    assert "shrink_prompt_then_retry" in (tmp_path / "provider_diagnostics.py").read_text(encoding="utf-8")


def test_curriculum_does_not_repeat_promoted_source_evolution(tmp_path):
    Path(tmp_path / "provider_diagnostics.py").write_text(
        _provider_source().replace(
            '    if "INVALID_MODEL_JSON" in normalized:\n',
            '    if "HTTP_413" in normalized:\n        return "shrink_prompt_then_retry"\n    if "INVALID_MODEL_JSON" in normalized:\n',
        ),
        encoding="utf-8",
    )

    report = run_source_evolution_curriculum(tmp_path)

    assert report["decision"] == "ALREADY_LEARNED"
    assert report["changed_files"] == []
