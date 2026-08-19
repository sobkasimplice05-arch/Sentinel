import json

from feedback_learning import AdaptiveFeedback


def inputs(content="fresh security data"):
    return (
        {"github": content + " " + ("x" * 100), "arxiv": content + " " + ("x" * 100)},
        {"mutations_suggested": ["optimize_defense_github", "optimize_defense_arxiv"]},
        {"source": "Sentinel-Local-Intentional", "decision": "AUTOMATIC_VALIDATION"},
    )


def test_first_new_observation_promotes_and_persists(tmp_path):
    engine = AdaptiveFeedback(
        db_filename=tmp_path / "memory.db",
        state_filename=tmp_path / "state.json",
        report_filename=tmp_path / "report.json",
    )

    result = engine.run_cycle(*inputs())

    assert result["decision"] == "PROMOTED"
    assert result["changed"] is True
    assert result["candidate_score"] >= result["baseline_score"]
    assert (tmp_path / "state.json").exists()
    assert (tmp_path / "report.json").exists()
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["successful_adaptations"] == 1
    assert state["policy"]["source_reliability"]["github"] > 0.5


def test_same_observation_is_not_counted_as_new_learning(tmp_path):
    engine = AdaptiveFeedback(
        db_filename=tmp_path / "memory.db",
        state_filename=tmp_path / "state.json",
        report_filename=tmp_path / "report.json",
    )
    first = engine.run_cycle(*inputs())
    second = engine.run_cycle(*inputs())

    assert first["decision"] == "PROMOTED"
    assert second["decision"] == "NO_CHANGE_NEEDED"
    assert second["changed"] is False
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["successful_adaptations"] == 1
    assert state["total_cycles"] == 1


def test_memory_is_reused_for_a_new_observation(tmp_path):
    engine = AdaptiveFeedback(
        db_filename=tmp_path / "memory.db",
        state_filename=tmp_path / "state.json",
        report_filename=tmp_path / "report.json",
    )
    first = engine.run_cycle(*inputs("first observation"))
    second = engine.run_cycle(*inputs("second observation"))

    assert first["decision"] == "PROMOTED"
    assert second["decision"] == "PROMOTED"
    assert second["policy_after"]["source_reliability"]["github"] > first["policy_after"]["source_reliability"]["github"]


def test_policy_validation_rejects_unsafe_threshold(tmp_path):
    engine = AdaptiveFeedback(
        db_filename=tmp_path / "memory.db",
        state_filename=tmp_path / "state.json",
        report_filename=tmp_path / "report.json",
    )
    engine.state["policy"]["confidence_threshold"] = 0.99
    result = engine.run_cycle(*inputs("new observation"))

    assert result["decision"] == "REJECTED"
    assert result["changed"] is False
    assert result["reason"] == "confidence_threshold hors limites [0.50, 0.90]"
