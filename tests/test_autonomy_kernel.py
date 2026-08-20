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


def test_no_change_persists_strategy_without_counting_mutation(tmp_path):
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

    assert first["should_persist"] is True
    assert (tmp_path / "autonomy_state.json").exists()
    state = json.loads((tmp_path / "autonomy_state.json").read_text())
    assert state["successful_experiments"] == 0
    assert state["strategy"]["last_outcome"] == "NO_CHANGE_NEEDED"


def test_autonomy_kernel_migrates_legacy_event_schema(tmp_path):
    import sqlite3

    db_path = tmp_path / "sentinel_memory.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE autonomy_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                observation_hash TEXT NOT NULL,
                decision TEXT NOT NULL,
                next_actions TEXT NOT NULL,
                strategy TEXT NOT NULL,
                report TEXT NOT NULL
            )
            """
        )
        connection.commit()

    kernel = AutonomyKernel(
        state_filename=tmp_path / "state.json",
        report_filename=tmp_path / "report.json",
        db_filename=db_path,
    )

    with sqlite3.connect(db_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(autonomy_events)")}

    assert {"baseline_score", "candidate_score"}.issubset(columns)
    assert kernel.db_filename == db_path


def test_repeated_no_change_does_not_require_commit(tmp_path, monkeypatch):
    monkeypatch.setenv("SENTINEL_HEARTBEAT_COMMIT_HOURS", "6")
    kernel = AutonomyKernel(
        state_filename=tmp_path / "state.json",
        report_filename=tmp_path / "report.json",
        db_filename=tmp_path / "memory.db",
    )
    first = kernel.advance(
        cycle_id="cycle-first",
        observation_hash="same-hash",
        decision="NO_CHANGE_NEEDED",
        baseline_score=0.6,
        candidate_score=0.6,
        source_count=2,
        feedback_report={},
    )
    second = kernel.advance(
        cycle_id="cycle-second",
        observation_hash="same-hash",
        decision="NO_CHANGE_NEEDED",
        baseline_score=0.6,
        candidate_score=0.6,
        source_count=2,
        feedback_report={},
    )

    assert first["should_persist"] is True
    assert second["should_persist"] is False
    assert second["heartbeat_due"] is False
