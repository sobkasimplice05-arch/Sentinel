from ai_matrix import AIMatrix


def test_matrix_rejects_unstructured_provider_response(monkeypatch):
    matrix = AIMatrix()
    monkeypatch.setattr(matrix.provider_engine, "_call_provider", lambda prompt, **kwargs: ("not json", "GOOGLE"))

    result = matrix.consult_brain({"intelligence_score": 42})

    assert result["decision"] == "INVALID_MODEL_JSON"
    assert result["confidence"] == 0.0
    assert result["source"] == "INVALID_MODEL_JSON"


def test_matrix_normalizes_structured_confidence(monkeypatch):
    matrix = AIMatrix()
    monkeypatch.setattr(
        matrix.provider_engine,
        "_call_provider",
        lambda prompt, **kwargs: (
            '{"decision":"MODEL_RECOMMENDATION","confidence":0.82,"hypothesis":"h","risks":[],"evidence":{"x":1}}',
            "GOOGLE",
        ),
    )

    result = matrix.consult_brain({"intelligence_score": 42})

    assert result["decision"] == "MODEL_RECOMMENDATION"
    assert result["confidence"] == 82.0
    assert result["source"] == "GOOGLE"
    assert result["evidence"] == {"x": 1}
