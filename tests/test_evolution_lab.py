import sqlite3

from evolution_lab import EvolutionLab


def test_code_promotion_requires_diff_validation_and_strict_gain(tmp_path):
    lab = EvolutionLab(tmp_path / "memory.db", tmp_path / "report.json")

    result = lab.record_experiment(
        cycle_id="cycle-1",
        observation_hash="obs-1",
        kind="self_modification",
        report={
            "decision": "PROMOTED",
            "baseline_score": 0.8,
            "candidate_score": 0.8,
            "changed_files": ["learning_engine.py"],
            "tests": {"compile_returncode": 0, "test_returncode": 0},
        },
    )

    assert result["decision"] == "REJECTED_NO_MEASUREMENT"
    assert result["code_promotion_verified"] is False
    assert result["measurable_gain"] is False

    with sqlite3.connect(tmp_path / "memory.db") as connection:
        row = connection.execute(
            "SELECT decision, rejection_reason, tests_passed FROM evolution_experiments"
        ).fetchone()
    assert row == ("REJECTED_NO_MEASUREMENT", "promotion annoncée sans gain strictement supérieur à la baseline", 1)


def test_code_promotion_rejects_forbidden_or_oversized_diff(tmp_path):
    lab = EvolutionLab(tmp_path / "memory.db", tmp_path / "report.json")

    result = lab.record_experiment(
        cycle_id="cycle-forbidden",
        observation_hash="obs-forbidden",
        kind="self_modification",
        report={
            "decision": "PROMOTED",
            "baseline_score": 0.1,
            "candidate_score": 0.9,
            "changed_files": [".github/workflows/sentinel.yml"],
            "tests": {"compile_returncode": 0, "test_returncode": 0},
        },
    )

    assert result["decision"] == "REJECTED_FORBIDDEN_DIFF"
    assert result["code_promotion_verified"] is False


def test_code_promotion_is_verified_only_after_strict_gain(tmp_path):
    lab = EvolutionLab(tmp_path / "memory.db", tmp_path / "report.json")

    result = lab.record_experiment(
        cycle_id="cycle-2",
        observation_hash="obs-2",
        kind="source_evolution",
        report={
            "decision": "PROMOTED",
            "baseline_score": 0.0,
            "candidate_score": 1.0,
            "changed_files": ["provider_diagnostics.py"],
            "compile_returncode": 0,
            "candidate_cases": {"case-a": True, "case-b": True},
        },
    )

    assert result["decision"] == "PROMOTED"
    assert result["code_promotion_verified"] is True
    assert result["measurable_gain"] is True


def test_record_cycle_separates_policy_from_code(tmp_path):
    lab = EvolutionLab(tmp_path / "memory.db", tmp_path / "report.json")

    report = lab.record_cycle(
        cycle_id="cycle-3",
        observation_hash="obs-3",
        feedback_report={
            "decision": "PROMOTED",
            "baseline_score": 0.7,
            "candidate_score": 0.7,
        },
        self_modification_report={
            "decision": "REJECTED",
            "reason": "REJECTED_NO_MEASUREMENT",
            "baseline_score": 0.0,
            "candidate_score": 0.0,
        },
        source_evolution_report={
            "decision": "ALREADY_LEARNED",
            "changed_files": [],
        },
    )

    assert len(report["experiments"]) == 3
    assert report["experiments"][0]["kind"] == "policy"
    assert report["experiments"][0]["code_promotion_verified"] is False
    assert report["summary"]["verified_code_promotions"] == 0
    assert (tmp_path / "report.json").exists()
