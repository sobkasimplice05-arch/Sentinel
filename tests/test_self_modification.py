import json

from self_modification import SelfModificationEngine


def test_model_unavailable_is_explicit_and_non_mutating(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "auto")
    for name in (
        "HF_API_KEY",
        "SELF_MODIFICATION_API_KEY",
        "MODEL_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
        "REPLICATE_API_TOKEN",
        "REPLICATE_API_KEY",
        "REPLICATE_MODEL",
        "REPLICATE_MODEL_VERSION",
        "SELF_MODIFICATION_MODEL_URL",
        "MODEL_API_URL",
        "OLLAMA_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)
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
    (tmp_path / "learning_engine.py").write_text("def evaluate_threats(data, policy=None):\n    return {}\n")
    engine = SelfModificationEngine(root=tmp_path)
    monkeypatch.setattr(engine, "_call_provider", lambda prompt, **kwargs: (None, "PROVIDER_ERROR:HTTPError"))

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
    (tmp_path / "learning_engine.py").write_text("def evaluate_threats(data, policy=None):\n    return {}\n")
    engine = SelfModificationEngine(root=tmp_path)
    monkeypatch.setattr(engine, "_call_provider", lambda prompt, **kwargs: (None, "PROVIDER_ERROR:HTTP_401"))

    result = engine.run_cycle(feedback={}, autonomy={})

    assert result["decision"] == "PROVIDER_ERROR"
    assert result["provider"] == "PROVIDER_ERROR:HTTP_401"


def test_prompt_is_segmented_to_one_target_file(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)
    sources = {
        "learning_engine.py": "A" * 2000,
        "feedback_learning.py": "B" * 2000,
    }
    prompt = engine._build_prompt(
        sources,
        {"decision": "NO_CHANGE_NEEDED"},
        {"next_actions": []},
        target_file="learning_engine.py",
    )

    assert "FILE: learning_engine.py" in prompt
    assert "FILE: feedback_learning.py" not in prompt
    assert len(prompt) <= engine.max_prompt_chars + 100


def test_ordered_targets_prefers_smallest_file(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)

    ordered = engine._ordered_targets(
        {
            "autonomy_kernel.py": "A" * 4000,
            "learning_engine.py": "L" * 400,
            "feedback_learning.py": "F" * 1800,
        }
    )

    assert ordered == ["learning_engine.py", "feedback_learning.py", "autonomy_kernel.py"]


def test_http_413_retries_with_compact_prompts(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_ENABLED", "true")
    (tmp_path / "learning_engine.py").write_text("def evaluate_threats(data, policy=None):\n    return {}\n")
    engine = SelfModificationEngine(root=tmp_path, allowed_files={"learning_engine.py"})
    calls = []

    def fake_provider(prompt, *, output_tokens=None):
        calls.append((len(prompt), output_tokens))
        return None, "PROVIDER_ERROR:HTTP_413"

    monkeypatch.setattr(engine, "_call_provider", fake_provider)
    result = engine.run_cycle(
        feedback={"context": "F" * 4000},
        autonomy={"context": "A" * 3000},
    )

    assert result["decision"] == "PROVIDER_ERROR"
    assert result["reason"] == "PROVIDER_ERROR:HTTP_413"
    assert len(calls) == 3
    assert calls[0][0] > calls[1][0]
    assert calls[0][1] > calls[1][1] > calls[2][1]
    assert [attempt["compact"] for attempt in result["attempts"]] == [False, True, True]


def test_extract_json_repairs_literal_newlines_in_file_content(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)
    raw = '{"hypothesis":"h","expected_gain":"g","files":[{"path":"learning_engine.py","content":"def f():\n    return 1\n"}]}'

    proposal = engine._parse_proposal(raw)

    assert proposal.files["learning_engine.py"] == "def f():\n    return 1\n"


def test_http_429_sets_provider_cooldown(tmp_path, monkeypatch):
    import requests

    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("SELF_MODIFICATION_COOLDOWN_SECONDS", "1800")

    class Response:
        status_code = 429
        headers = {"retry-after": "120"}

    error = requests.HTTPError("rate limited")
    error.response = Response()

    def fail_post(*args, **kwargs):
        raise error

    monkeypatch.setattr("self_modification.requests.post", fail_post)
    engine = SelfModificationEngine(root=tmp_path)
    raw, provider = engine._call_provider("return json")

    assert raw is None
    assert provider == "PROVIDER_ERROR:HTTP_429"
    assert engine._provider_on_cooldown("groq") is True
    raw, provider = engine._call_provider("return json")
    assert raw is None
    assert provider == "PROVIDER_COOLDOWN:GROQ"


def test_google_gemini_provider_extracts_structured_text(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "google")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-test-key")
    monkeypatch.setenv("GOOGLE_MODEL", "gemini-test")

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": '{"files":[]}'}]}}]}

    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["json"] = kwargs["json"]
        return Response()

    monkeypatch.setattr("self_modification.requests.post", fake_post)
    engine = SelfModificationEngine(root=tmp_path)

    raw, provider = engine._call_provider("return json")

    assert raw == '{"files":[]}'
    assert provider == "GOOGLE"
    assert captured["url"].endswith("/models/gemini-test:generateContent")
    assert captured["headers"]["x-goog-api-key"] == "google-test-key"
    assert captured["json"]["generationConfig"]["responseMimeType"] == "application/json"


def test_ollama_provider_targets_local_qwen_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/api/generate")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": '{"files":[]}'}

    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return Response()

    monkeypatch.setattr("self_modification.requests.post", fake_post)
    engine = SelfModificationEngine(root=tmp_path)

    raw, provider = engine._call_provider("return json")

    assert raw == '{"files":[]}'
    assert provider == "OLLAMA"
    assert captured["url"] == "http://127.0.0.1:11434/api/generate"
    assert captured["json"]["model"] == "qwen2.5-coder:7b"
    assert captured["json"]["stream"] is False


def test_auto_provider_uses_google_after_groq_cooldown(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "auto")
    monkeypatch.setenv("GROQ_API_KEY", "groq-test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-test-key")
    engine = SelfModificationEngine(root=tmp_path)
    engine._set_provider_cooldown("groq", retry_after=1800)

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": '{"files":[]}'}]}}]}

    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        return Response()

    monkeypatch.setattr("self_modification.requests.post", fake_post)
    raw, provider = engine._call_provider("return json")

    assert raw == '{"files":[]}'
    assert provider == "GOOGLE"
    assert "generativelanguage.googleapis.com" in captured["url"]
    assert engine._provider_on_cooldown("groq") is True


def test_auto_provider_falls_back_after_http_429(tmp_path, monkeypatch):
    import requests

    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "auto")
    monkeypatch.setenv("GROQ_API_KEY", "groq-test-key")
    monkeypatch.setenv("HF_API_KEY", "hf-test-key")
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_GEMINI_API_KEY", "NVIDIA_API_KEY", "MODEL_API_KEY", "MODEL_API_URL", "SELF_MODIFICATION_MODEL_URL", "OLLAMA_BASE_URL"):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "learning_engine.py").write_text("def evaluate_threats(data, policy=None):\n    return {}\n")

    class RateLimitResponse:
        status_code = 429
        headers = {"retry-after": "120"}

    rate_limit_error = requests.HTTPError("rate limited")
    rate_limit_error.response = RateLimitResponse()

    class SuccessResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return [{"generated_text": '{"files":[]}'}]

    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        if "api.groq.com" in url:
            raise rate_limit_error
        return SuccessResponse()

    monkeypatch.setattr("self_modification.requests.post", fake_post)
    engine = SelfModificationEngine(root=tmp_path, allowed_files={"learning_engine.py"})

    result = engine.run_cycle(feedback={}, autonomy={})

    assert result["decision"] == "NO_CHANGE_PROPOSED"
    assert any("api.groq.com" in url for url in calls)
    assert any("api-inference.huggingface.co" in url for url in calls)
    assert [attempt["provider"] for attempt in result["attempts"]] == ["PROVIDER_ERROR:HTTP_429", "HUGGINGFACE_INFERENCE"]


def test_cloudflare_workers_ai_provider_extracts_response(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "cloudflare")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "cf-test-token")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "account-test")
    monkeypatch.setenv("CLOUDFLARE_MODEL", "@cf/qwen/qwen2.5-coder-32b-instruct")

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"success": True, "result": {"response": '{"files":[]}'}}

    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["json"] = kwargs["json"]
        return Response()

    monkeypatch.setattr("self_modification.requests.post", fake_post)
    engine = SelfModificationEngine(root=tmp_path)

    raw, provider = engine._call_provider("return json")

    assert raw == '{"files":[]}'
    assert provider == "CLOUDFLARE"
    assert captured["url"].endswith("/accounts/account-test/ai/run/@cf/qwen/qwen2.5-coder-32b-instruct")
    assert captured["headers"]["Authorization"] == "Bearer cf-test-token"
    assert captured["json"]["response_format"] == {"type": "json_object"}


def test_cloudflare_invalid_json_gets_one_bounded_repair_attempt(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "cloudflare")
    (tmp_path / "learning_engine.py").write_text("def evaluate_threats(data, policy=None):\n    return {}\n")
    engine = SelfModificationEngine(root=tmp_path, allowed_files={"learning_engine.py"})
    calls = []
    invalid = '{"hypothesis":"h","expected_gain":"g","files":[{"path":"learning_engine.py","content":"def f():\n    return "bad"\n"}]}'

    def fake_provider(prompt, *, output_tokens=None):
        calls.append((prompt, output_tokens))
        if len(calls) == 1:
            return invalid, "CLOUDFLARE"
        return '{"hypothesis":"h","expected_gain":"g","files":[]}', "CLOUDFLARE"

    monkeypatch.setattr(engine, "_call_provider", fake_provider)
    result = engine.run_cycle(feedback={}, autonomy={})

    assert result["decision"] == "NO_CHANGE_PROPOSED"
    assert len(calls) == 2
    assert "Réponse invalide à réparer" in calls[1][0]
    assert result["attempts"][0]["repair_provider"] == "CLOUDFLARE"


def test_auto_provider_falls_back_after_empty_cloudflare_response(tmp_path, monkeypatch):
    monkeypatch.setenv("SELF_MODIFICATION_PROVIDER", "auto")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "cf-test-token")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "account-test")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-test-key")
    for name in ("GROQ_API_KEY", "HF_API_KEY", "NVIDIA_API_KEY", "MODEL_API_KEY", "MODEL_API_URL", "SELF_MODIFICATION_MODEL_URL", "OLLAMA_BASE_URL"):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "learning_engine.py").write_text("def evaluate_threats(data, policy=None):\n    return {}\n")

    class EmptyCloudflareResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"success": True, "result": {}}

    class GoogleResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": '{"hypothesis":"h","expected_gain":"g","files":[]}' }]}}]}

    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        if "api.cloudflare.com" in url:
            return EmptyCloudflareResponse()
        return GoogleResponse()

    monkeypatch.setattr("self_modification.requests.post", fake_post)
    engine = SelfModificationEngine(root=tmp_path, allowed_files={"learning_engine.py"})
    result = engine.run_cycle(feedback={}, autonomy={})

    assert result["decision"] == "NO_CHANGE_PROPOSED"
    assert [attempt["provider"] for attempt in result["attempts"]] == ["EMPTY_CLOUDFLARE_RESPONSE", "GOOGLE"]
    assert engine._provider_on_cooldown("cloudflare") is True
    assert any("api.cloudflare.com" in url for url in calls)
    assert any("generativelanguage.googleapis.com" in url for url in calls)


def test_passing_candidate_without_measured_gain_is_not_promoted(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)
    proposal = engine._parse_proposal(
        '{"hypothesis":"cleanup","expected_gain":"none","files":[{"path":"learning_engine.py","content":"print(1)"}]}'
    )

    score = engine._score(
        {"compile_returncode": 0, "test_returncode": 0},
        proposal,
    )

    assert score == 0.0


def test_structure_rejects_dynamic_code_execution(tmp_path):
    engine = SelfModificationEngine(root=tmp_path)
    proposal = engine._parse_proposal(
        '{"hypothesis":"bad","expected_gain":"none","files":[{"path":"learning_engine.py","content":"exec(\\\"print(1)\\\")"}]}'
    )

    valid, reason = engine._validate_structure(proposal)

    assert valid is False
    assert reason == "forbidden_process_control"
