from daily_metrics_report import render_discord, send_discord


def test_render_discord_contains_key_metrics():
    metrics = {
        "git": {"commit_count": 4, "autonomous_commit_count": 2},
        "feedback": {"decision": "PROMOTED", "baseline_score": 0.75, "candidate_score": 0.85, "provider": "GROQ"},
        "autonomy": {"cycle_number": 12, "confidence": 0.65, "next_actions": ["measure", "observe"]},
        "agent_general": {"objective": "improve_transfer", "transfer_verified": False},
        "self_modification": {"decision": "PROMOTED", "provider": "GROQ", "changed_files": ["autonomy_kernel.py"], "candidate_score": 0.85},
    }

    text = render_discord(metrics)

    assert "PROMOTED" in text
    assert "autonomy_kernel.py" in text
    assert "0.75 → 0.85" in text


def test_send_discord_uses_secret_without_printing_it(monkeypatch):
    secret = "https://discord.com/api/webhooks/test/token"
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

    monkeypatch.setenv("WEBTOON", secret)
    monkeypatch.delenv("SENTINEL_DISCORD_WEBHOOK", raising=False)
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["payload"] = kwargs["json"]
        return Response()

    monkeypatch.setattr("daily_metrics_report.requests.post", fake_post)
    send_discord("test report")

    assert captured["url"] == secret
    assert captured["payload"] == {"content": "test report"}
