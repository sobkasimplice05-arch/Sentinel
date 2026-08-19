import json

from autonomy_kernel import AutonomyKernel


def test_autonomy_kernel_plans_after_promotion(tmp_path):
    kernel = AutonomyKernel(
        state_filename=tmp_path / "autonomy_state.json",
        report_filename=tmp_path / "autonomy_report.json",
        db_filename=tmp_path / "memory.db",
    )
    result = kernel.advance(
        cycle_id="cycle-1",
        observation_hash="hash-1",
        decision="PROMOTED",
        baseline_score=0.6,
        candidate_score=0.7,
        source_count=2,
        feedback_report={"decision": "PROMOTED"},
    )

    assert result["autonomy_mode"] == "MAXIMUM_CONTROLLED"
    assert result["next_actions"]
    assert "reuse_promoted_policy_next_cycle" in result["next_actions"]
    state = json.loads((tmp_path / "autonomy_state.json").read_text())
    assert state["cycle_number"] == 1
    assert state["successful_experiments"] == 1
    assert state["strategy"]["last_outcome"] == "PROMOTED"


def test_autonomy_kernel_records_rejection_as_future_work(tmp_path):
    kernel = AutonomyKernel(
        state_filename=tmp_path / "autonomy_state.json",
        report_filename=tmp_path / "autonomy_report.json",
        db_filename=tmp_path / "memory.db",
    )
    result = kernel.advance(
        cycle_id="cycle-2",
        observation_hash="hash-2",
        decision="REJECTED",
        baseline_score=0.7,
        candidate_score=0.4,
        source_count=1,
        feedback_report={"decision": "REJECTED"},
    )

    assert result["strategy"]["last_outcome"] == "REJECTED"
    assert "record_rejection_reason" in result["next_actions"]
    state = json.loads((tmp_path / "autonomy_state.json").read_text())
    assert state["rejected_experiments"] == 1


def test_no_change_is_not_persisted_until_heartbeat(tmp_path):
    kernel = AutonomyKernel(
        state_filename=tmp_path / "autonomy_state.json",
        report_filename=tmp_path / "autonomy_report.json",
        db_filename=tmp_path / "memory.db",
    )
    first = kernel.advance(
        cycle_id="cycle-3",
        observation_hash="hash-3",
        decision="NO_CHANGE_NEEDED",
        baseline_score=0.6,
        candidate_score=0.6,
        source_count=2,
        feedback_report={"decision": "NO_CHANGE_NEEDED"},
    )

    assert first["should_persist"] is False
    assert not (tmp_path / "autonomy_state.json").exists()
