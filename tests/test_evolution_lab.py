import sqlite3
import subprocess

from evolution_lab import EvolutionLab


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _git_output(repo, *args):
    return _git(repo, *args).stdout.strip()


def _init_repo(path):
    path.mkdir()
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "test@example.invalid")
    _git(path, "config", "user.name", "Evolution Lab Test")
    (path / "learning_engine.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(path, "add", ".")
    _git(path, "commit", "-m", "baseline")
    _git(path, "branch", "-M", "main")


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
    assert result["coverage_complete"] is True


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
    assert report["summary"]["open_error_patterns"] >= 1
    assert (tmp_path / "report.json").exists()


def test_transaction_waits_for_review_then_absorbs_on_observed_branch(tmp_path):
    repo = tmp_path / "repo"
    _init_repo(repo)
    lab = EvolutionLab(repo / "memory.db", repo / "report.json", repo)
    base = _git_output(repo, "rev-parse", "HEAD")

    tx = lab.start_transaction(
        cycle_id="cycle-tx",
        objective="Improve transfer evidence",
        observation_hash="obs-tx",
    )
    assert tx["status"] == "started"
    assert tx["base_commit"] == base

    _git(repo, "switch", "-c", "candidate")
    (repo / "learning_engine.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "learning_engine.py")
    _git(repo, "commit", "-m", "candidate")
    candidate = _git_output(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "main")

    assert lab.mark_commit(
        cycle_id="cycle-tx",
        candidate_commit=candidate,
        candidate_branch="evolution-lab/test",
        evidence={"review": "passed"},
    )
    pending = lab.reconcile_pending()
    assert pending["absorbed"] == 0
    assert pending["pending"] == 1

    _git(repo, "switch", "candidate")
    absorbed = EvolutionLab(repo / "memory.db", repo / "report.json", repo).reconcile_pending()
    assert absorbed["absorbed"] == 1
    assert absorbed["pending"] == 0

    with sqlite3.connect(repo / "memory.db") as connection:
        status = connection.execute(
            "SELECT status, restart_verified, outcome FROM evolution_transactions WHERE cycle_id = 'cycle-tx'"
        ).fetchone()
        checkpoint_count = connection.execute(
            "SELECT COUNT(*) FROM evolution_checkpoints WHERE cycle_id = 'cycle-tx' AND status = 'absorbed'"
        ).fetchone()[0]
    assert status == ("absorbed", 1, "absorbed")
    assert checkpoint_count == 1


def test_error_pattern_is_fingerprint_deduplicated_and_recurrent(tmp_path):
    lab = EvolutionLab(tmp_path / "memory.db", tmp_path / "report.json")

    first = lab.record_pattern(summary="Provider timeout during benchmark", category="provider")
    second = lab.record_pattern(summary="  Provider   timeout during benchmark ", category="provider")

    assert first["fingerprint"] == second["fingerprint"]
    assert second["count"] == 2
    assert "count=2" in lab.pattern_digest()


def test_coverage_manifest_hashes_required_surfaces(tmp_path):
    (tmp_path / "learning_engine.py").write_text("VALUE = 1\n", encoding="utf-8")
    lab = EvolutionLab(tmp_path / "memory.db", tmp_path / "report.json", tmp_path)

    manifest = lab.coverage_manifest(["learning_engine.py", "missing.py"])

    assert manifest["complete"] is False
    assert manifest["observed_files"][0]["path"] == "learning_engine.py"
    assert manifest["observed_files"][0]["sha256"] == __import__("hashlib").sha256(b"VALUE = 1\n").hexdigest()
    assert manifest["omitted"] == [{"path": "missing.py", "reason": "missing"}]



def test_code_promotion_rejects_incomplete_review_coverage(tmp_path):
    lab = EvolutionLab(tmp_path / "memory.db", tmp_path / "report.json")
    result = lab.record_experiment(
        cycle_id="cycle-coverage",
        observation_hash="obs-coverage",
        kind="self_modification",
        report={
            "decision": "PROMOTED",
            "baseline_score": 0.4,
            "candidate_score": 0.8,
            "changed_files": ["learning_engine.py"],
            "tests": {"compile_returncode": 0, "test_returncode": 0},
            "coverage": {"complete": False, "omitted": [{"path": "feedback_learning.py", "reason": "not_reviewed"}]},
        },
    )
    assert result["decision"] == "REJECTED_INCOMPLETE_COVERAGE"
    assert result["code_promotion_verified"] is False
