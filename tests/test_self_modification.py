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


def test_provider_error_is_reported_separately(tmp_path, monkeypatch):
    engine = SelfModificationEngine(root=tmp_path)
    monkeypatch.setattr(engine, "_call_provider", lambda prompt: (None, "PROVIDER_ERROR:HTTPError"))

    result = engine.run_cycle(feedback={}, autonomy={})

    assert result["decision"] == "PROVIDER_ERROR"
    assert result["provider"] == "PROVIDER_ERROR:HTTPError"


def test_openai_compatible_provider_extracts_message(tmp_path, monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"files":[]}'}}]}

    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.delenv("SELF_MODIFICATION_MODEL_URL", raising=False)
    monkeypatch.setattr("self_modification.requests.post", lambda *args, **kwargs: Response())
    engine = SelfModificationEngine(root=tmp_path)

    raw, provider = engine._call_provider("return json")

    assert raw == '{"files":[]}'
    assert provider == "GROQ"


def test_auto_provider_prefers_nvidia_key(tmp_path, monkeypatch):
    engine = SelfModificationEngine(root=tmp_path)
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "auto")
    monkeypatch.setenv("NVIDIA_API_KEY", "nvidia-test-key")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("HF_API_KEY", raising=False)

    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"files":[]}'}}]}

    def fake_post(url, **kwargs):
        captured["url"] = url
        return Response()

    monkeypatch.setattr("self_modification.requests.post", fake_post)
    raw, provider = engine._call_provider("return json")

    assert captured["url"] == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert provider == "NVIDIA"
    assert raw == '{"files":[]}'


def test_http_provider_error_keeps_status_code(tmp_path, monkeypatch):
    import requests

    class Response:
        status_code = 401

    error = requests.HTTPError("unauthorized")
    error.response = Response()
    engine = SelfModificationEngine(root=tmp_path)
    monkeypatch.setattr(engine, "_call_provider", lambda prompt: (None, "PROVIDER_ERROR:HTTP_401"))

    result = engine.run_cycle(feedback={}, autonomy={})

    assert result["decision"] == "PROVIDER_ERROR"
    assert result["provider"] == "PROVIDER_ERROR:HTTP_401"
