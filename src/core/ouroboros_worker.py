import asyncio
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import List

from loguru import logger
from src.orchestrator.llm_orchestrator import LLMOrchestrator
from src.core.self_audit import SelfAudit

DISCORD_WEBHOOK_URL = "https://discord.com"


def _commit_autonomous_patch() -> bool:
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(ouroboros): autonomous patch applied and verified"],
            check=True,
        )
        subprocess.run(["git", "push", "origin", "main"], check=True)
        logger.info("Ouroboros Worker: Changes committed and pushed automatically.")
        return True
    except subprocess.CalledProcessError as exc:
        logger.exception(f"Ouroboros Worker: Git commit/push failed: {exc}")
        return False
    except Exception as exc:
        logger.exception(f"Ouroboros Worker: Unexpected git error: {exc}")
        return False


async def send_discord_alert(title: str, description: str, color: int) -> None:
    webhook_url = DISCORD_WEBHOOK_URL
    payload = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        ]
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        await asyncio.to_thread(urllib.request.urlopen, request)
        logger.info("Ouroboros Worker: Discord alert envoyé avec succès.")
    except urllib.error.HTTPError as exc:
        logger.exception(f"Ouroboros Worker: Discord webhook HTTP error: {exc.code} - {exc.reason}")
    except urllib.error.URLError as exc:
        logger.exception(f"Ouroboros Worker: Discord webhook connection error: {exc.reason}")
    except Exception as exc:
        logger.exception(f"Ouroboros Worker: Failed to send Discord alert: {exc}")


async def start_periodic_audit() -> None:
    """Démarre une boucle Ouroboros qui audit les sources toutes les 5 minutes."""
    logger.info("Ouroboros Worker: Démarrage du worker de nuit...")

    orchestrator = LLMOrchestrator(test_mode=os.getenv("TEST_MODE", "false").lower() == "true")
    self_audit = SelfAudit(orchestrator)
    source_root = Path(__file__).resolve().parents[2]

    while True:
        try:
            logger.info("Ouroboros Worker: Début de l'auto-analyse cyclique...")
            source_files: List[str] = [
                str(path)
                for path in source_root.rglob("*.py")
                if path.is_file()
                and path.name != "__init__.py"
                and "venv" not in path.parts
                and ".venv" not in path.parts
                and "site-packages" not in path.parts
                and ".git" not in path.parts
            ]
            logger.info(f"Ouroboros Worker: {len(source_files)} fichiers sources détectés")

            result = await asyncio.to_thread(self_audit.audit_sources, source_files, True)
            logger.info("Ouroboros Worker: Auto-analyse terminée")
            logger.info(f"Ouroboros Worker: Résultats: {result}")

            commit_performed = False
            if result.get("success") and any(
                item.get("auto_rewritten", False) for item in result.get("results", [])
            ):
                logger.info("Ouroboros Worker: Validated autonomous changes detected, committing to Git.")
                commit_performed = await asyncio.to_thread(_commit_autonomous_patch)
                if commit_performed:
                    try:
                        await send_discord_alert(
                            title="📜 Sentinelle - Patch autonome appliqué",
                            description="Sentinel a validé et commité automatiquement une amélioration de code. Le déploiement autonome a été réalisé avec succès.",
                            color=65280,
                        )
                    except Exception as exc:
                        logger.exception(f"Ouroboros Worker: Erreur lors de l'envoi de l'alerte Discord de commit: {exc}")

            if not commit_performed:
                try:
                    await send_discord_alert(
                        title="🔎 Sentinelle en veille",
                        description="Système stable, Sentinel veille. Aucun code n'a été modifié lors de ce cycle.",
                        color=255,
                    )
                except Exception as exc:
                    logger.exception(f"Ouroboros Worker: Erreur lors de l'envoi de l'alerte Discord de veille: {exc}")
        except Exception as exc:
            logger.exception(f"Ouroboros Worker: Erreur durant l'auto-analyse cyclique: {exc}")

        logger.info("Ouroboros Worker: Attente avant la prochaine analyse cyclique de 5 minutes...")
        await asyncio.sleep(300)
