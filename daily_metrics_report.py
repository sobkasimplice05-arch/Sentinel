"""Génère et envoie une synthèse quotidienne des métriques Sentinel."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

from evolution_lab import EvolutionLab

ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "daily_metrics_report.json"
REPORT_MD = ROOT / "daily_metrics_report.md"


def load_json(name: str) -> dict[str, Any]:
    path = ROOT / name
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def git_recent() -> dict[str, Any]:
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    result = subprocess.run(
        ["git", "log", "--since", since, "--pretty=format:%H%x09%s", "--name-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    source_names = {"learning_engine.py", "feedback_learning.py", "autonomy_kernel.py", "self_modification.py"}
    commits: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in lines:
        if "\t" in line:
            if current is not None:
                commits.append(current)
            sha, subject = line.split("\t", 1)
            current = {
                "sha": sha,
                "subject": subject,
                "autonomous": "FEEDBACK" in subject.upper(),
                "source_changed": False,
                "files": [],
            }
        elif current is not None:
            current["files"].append(line)
            if line in source_names:
                current["source_changed"] = True
    if current is not None:
        commits.append(current)
    autonomous = [commit for commit in commits if commit["autonomous"]]
    source_promotions = [commit for commit in autonomous if commit["source_changed"]]
    source_files = sorted({
        path
        for commit in commits
        for path in commit["files"]
        if path in source_names
    })
    return {
        "commit_count": len(commits),
        "autonomous_commit_count": len(autonomous),
        "memory_only_commit_count": max(0, len(autonomous) - len(source_promotions)),
        "source_promotion_count": len(source_promotions),
        "latest_commit": f"{commits[0]['sha']}\t{commits[0]['subject']}" if commits else "Aucun commit sur les dernières 24 heures",
        "source_files_changed": source_files,
    }


def sqlite_metrics() -> dict[str, Any]:
    path = ROOT / "sentinel_memory.db"
    if not path.exists():
        return {"available": False}
    metrics: dict[str, Any] = {"available": True}
    try:
        with sqlite3.connect(path) as connection:
            tables = {
                row[0]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            for table, key in (
                ("autonomy_events", "autonomy_events"),
                ("agent_episodes", "agent_episodes"),
                ("agent_skills", "agent_skills"),
                ("agent_transfer_tests", "agent_transfer_tests"),
            ):
                if table in tables:
                    metrics[key] = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except sqlite3.Error as exc:
        metrics["error"] = type(exc).__name__
    return metrics


def evolution_metrics() -> dict[str, Any]:
    try:
        return EvolutionLab().summary()
    except (OSError, sqlite3.Error, TypeError, ValueError):
        return {"available": False}


def collect_metrics() -> dict[str, Any]:
    feedback = load_json("feedback_report.json")
    autonomy = load_json("sentinel_autonomy_state.json")
    agent = load_json("agent_general_state.json")
    self_mod = load_json("self_modification_report.json")
    cooldowns = load_json("self_modification_provider_cooldown.json")
    now_timestamp = datetime.now(timezone.utc).timestamp()
    active_cooldowns = sorted(
        str(provider).upper()
        for provider, until in cooldowns.items()
        if isinstance(until, (int, float)) and float(until) > now_timestamp
    )
    self_mod_decision = self_mod.get("decision", "UNKNOWN")
    self_mod_provider = self_mod.get("provider", "UNKNOWN")
    if active_cooldowns:
        self_mod_decision = "PROVIDER_COOLDOWN"
        self_mod_provider = ", ".join(active_cooldowns)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": "24h",
        "git": git_recent(),
        "feedback": {
            "decision": feedback.get("decision", "UNKNOWN"),
            "baseline_score": feedback.get("baseline_score"),
            "candidate_score": feedback.get("candidate_score"),
            "provider": feedback.get("provider", feedback.get("ai_source", "UNKNOWN")),
        },
        "autonomy": {
            "cycle_number": autonomy.get("cycle_number", 0),
            "confidence": autonomy.get("strategy", {}).get("confidence"),
            "successful_experiments": autonomy.get("successful_experiments", 0),
            "rejected_experiments": autonomy.get("rejected_experiments", 0),
            "next_actions": autonomy.get("next_actions", []),
        },
        "agent_general": {
            "mode": agent.get("mode", "UNKNOWN"),
            "cycle_number": agent.get("cycle_number", 0),
            "transfer_verified": agent.get("transfer_verified", False),
            "objective": agent.get("current_objective", {}).get("title", "UNKNOWN"),
        },
        "active_cooldowns": active_cooldowns,
        "self_modification": {
            "decision": self_mod_decision,
            "provider": self_mod_provider,
            "changed_files": self_mod.get("changed_files", []),
            "candidate_score": self_mod.get("candidate_score"),
            "attempt_count": len(self_mod.get("attempts", [])),
        },
        "evolution_lab": evolution_metrics(),
        "sqlite": sqlite_metrics(),
    }


def render_discord(metrics: dict[str, Any]) -> str:
    git = metrics["git"]
    feedback = metrics["feedback"]
    autonomy = metrics["autonomy"]
    agent = metrics["agent_general"]
    mutation = metrics["self_modification"]
    evolution = metrics.get("evolution_lab", {})
    changed = ", ".join(mutation["changed_files"]) or "aucun"
    next_actions = ", ".join(autonomy["next_actions"][:2]) or "aucune"
    text = (
        "**Sentinel — synthèse des dernières 24 h**\n"
        f"Cycle autonomie : **{autonomy['cycle_number']}** | confiance : **{autonomy['confidence']}**\n"
        f"Auto-évolution source : **{mutation['decision']}** | fournisseur : `{mutation['provider']}`\n"
        f"Cooldowns actifs : `{', '.join(metrics.get('active_cooldowns', [])) or 'aucun'}`\n"
        f"Fichiers promus : `{changed}` | score candidat : **{mutation['candidate_score']}**\n"
        f"Feedback : **{feedback['decision']}** | baseline → candidat : `{feedback['baseline_score']} → {feedback['candidate_score']}`\n"
        f"Objectif agent général : `{agent['objective']}` | transfert vérifié : **{agent['transfer_verified']}**\n"
        f"Commits sur 24 h : **{git.get('commit_count', 0)}** | mémoire seule : **{git.get('memory_only_commit_count', 0)}** | code promu : **{git.get('source_promotion_count', 0)}**\n"
        f"Evolution Lab : absorbées **{evolution.get('absorbed_after_restart', 0)}** | revue **{evolution.get('awaiting_review', 0)}** | classes d’erreurs **{evolution.get('open_error_patterns', 0)}**\n"
        f"Prochaines actions : `{next_actions}`"
    )
    return text[:1950]


def send_discord(content: str) -> None:
    webhook = (
        os.getenv("SENTINEL_DISCORD_WEBHOOK")
        or os.getenv("DISCORD_WEBHOOK_URL")
        or os.getenv("WEBTOON")
    )
    if not webhook:
        raise RuntimeError("Secret Discord absent: SENTINEL_DISCORD_WEBHOOK, DISCORD_WEBHOOK_URL ou WEBTOON")
    if not webhook.startswith(("https://discord.com/api/webhooks/", "https://discordapp.com/api/webhooks/")):
        raise RuntimeError("Le secret Discord ne ressemble pas à une URL de webhook Discord")
    response = requests.post(webhook, json={"content": content}, timeout=15)
    response.raise_for_status()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--send-discord", action="store_true")
    parser.add_argument("--require-discord", action="store_true")
    args = parser.parse_args()
    metrics = collect_metrics()
    discord_text = render_discord(metrics)
    REPORT_JSON.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(discord_text + "\n", encoding="utf-8")
    if args.send_discord:
        try:
            send_discord(discord_text)
            print("Discord report sent")
        except (OSError, RuntimeError, TypeError, ValueError, requests.RequestException) as exc:
            print(f"Discord report failed: {type(exc).__name__}")
            if args.require_discord:
                return 1
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
