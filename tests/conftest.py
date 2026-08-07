# tests/conftest.py
import pytest

class _MockResponse:
    def __init__(self, text, status_code=200):
        self._text = text
        self.status_code = status_code

    def json(self):
        return {"response": self._text}


@pytest.fixture(autouse=True)
def mock_requests_post(monkeypatch):
    """Remplace requests.post par une fonction factice pour les tests.

    Cette fixture s'applique automatiquement à tous les tests et renvoie
    une réponse déterministe adaptée aux attentes de LLMOrchestrator.
    """
    def _fake_post(url, json=None, timeout=None, **kwargs):
        prompt = (json or {}).get("prompt", "")
        # Réponse déterministe utilisée par les tests
        text = f"Mocked response to instruction: {prompt}"
        return _MockResponse(text)

    monkeypatch.setattr("requests.post", _fake_post)
    yield
