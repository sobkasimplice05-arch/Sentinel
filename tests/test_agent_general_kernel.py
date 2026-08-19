import json

from agent_general_kernel import GeneralAgentKernel


def test_agent_kernel_creates_objective_and_multistep_plan(tmp_path):
    kernel = GeneralAgentKernel(
        state_filename=tmp_path / "agent_state.json",
        report_filename=tmp_path / "agent_report.json",
        db_filename=tmp_path / "memory.db",
    )
    objective = kernel.select_objective(["github", "arxiv"])
    plan = kernel.build_plan(objective, ["observation", "source_modification"])
    report = kernel.record_cycle(
        objective=objective,
        plan=plan,
        observation_hash="hash-1",
        feedback={"decision": "PROMOTED", "candidate_score": 0.66},
        self_modification={"decision": "MODEL_UNAVAILABLE"},
    )

    assert objective["status"] == "PENDING"
    assert len(plan) == 5
    assert plan[2]["action"] == "execute_tools_or_candidate_patch_in_isolation"
    assert report["transfer_verified"] is False
    state = json.loads((tmp_path / "agent_state.json").read_text())
    assert state["cycle_number"] == 1
    assert state["current_objective_id"] == objective["id"]


def test_transfer_requires_unseen_variant_and_threshold(tmp_path):
    kernel = GeneralAgentKernel(
        state_filename=tmp_path / "agent_state.json",
        report_filename=tmp_path / "agent_report.json",
        db_filename=tmp_path / "memory.db",
    )
    rejected = kernel.evaluate_transfer(
        "observation_skill",
        [{"name": "variant_a", "score": 0.60}, {"name": "variant_b", "score": 0.62}],
    )
    promoted = kernel.evaluate_transfer(
        "observation_skill",
        [{"name": "variant_c", "score": 0.80}, {"name": "variant_d", "score": 0.75}],
    )

    assert rejected["decision"] == "REJECTED"
    assert promoted["decision"] == "PROMOTED"
    assert promoted["skill"]["transfer_score"] == 0.775
    assert kernel.state["transfer_verified"] is True
