# scripts/run_demo.py
"""Script to run Sentinel demo locally without a running LLM.
It monkeypatches requests.post to return deterministic mock responses so you can test the full pipeline.

Usage:
  python scripts/run_demo.py
"""

import requests
from types import SimpleNamespace

class _MockResponse:
    def __init__(self, text, status_code=200):
        self._text = text
        self.status_code = status_code

    def json(self):
        return {"response": self._text}


def _fake_post(url, json=None, timeout=None, **kwargs):
    prompt = (json or {}).get("prompt", "")
    text = f"[mocked] Response to: {prompt}"
    return _MockResponse(text)

# Patch requests.post globally for this script
requests.post = _fake_post

if __name__ == "__main__":
    from src.sentinel_main import demo
    demo()
