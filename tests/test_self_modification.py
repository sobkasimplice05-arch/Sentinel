import json

from self_modification import SelfModificationEngine


def test_model_unavailable_is_explicit_and_non_mutating(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_API_KEY", raising=False)
    monkeypatch.delenv("SELF_MODIFICATION_API_KEY", raising=False)
    monkeypatch.delenv("SELF_MODIFICATION_MODEL_URL", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    engine = SelfModificationEngine(root=tmp_path)
    result = engine.run_cycle(feedback={"decision": "NO_CHANGE_NEEDED"}, autonomy={"next_actions": []})

    assert result["decision"] == "MODEL_UNAVAILABLE"
    assert json.loads((tmp_path / "self_modification_report.json").read_text())["decision"] == "MODEL_UNAVAILABLE"


def test_parser_accepts_only_allowed_source_files(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)
    proposal = engine._parse_proposal(
        '{"hypothesis":"improve","expected_gain":"tests","files":[{"path":"learning_engine.py","content":"print(1)"}]}'
    )

    assert proposal.files == {"learning_engine.py": "print(1)"}


def test_parser_rejects_path_escape(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)

    try:
        engine._parse_proposal(
            '{"hypothesis":"escape","expected_gain":"none","files":[{"path":"../main.py","content":"print(1)"}]}'
        )
    except ValueError as error:
        assert "non autorisé" in str(error)
    else:
        raise AssertionError("path escape should be rejected")


def test_structure_rejects_unbounded_side_effects(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)
    proposal = engine._parse_proposal(
        '{"hypothesis":"bad","expected_gain":"none","files":[{"path":"learning_engine.py","content":"import subprocess"}]}'
    )

    valid, reason = engine._validate_structure(proposal)
    assert valid is False
    assert reason == "forbidden_process_control"
