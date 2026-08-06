import asyncio
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import List

from loguru import logger
from src.orchestrator.llm_orchestrator import LLMOrchestrator
from src.core.self_audit import SelfAudit

DISCORD_WEBHOOK_URL = "REPLACE_ME_NOW"
PENDING_DISCORD_ALERTS_PATH = Path(__file__).resolve().parents[1] / "logging" / "pending_discord_alerts.json"
failed_alerts_queue: List[dict] = []


def _save_failed_alerts_queue() -> None:
    try:
        PENDING_DISCORD_ALERTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with PENDING_DISCORD_ALERTS_PATH.open("w", encoding="utf-8") as file:
            json.dump(failed_alerts_queue, file, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.exception(
            f"Ouroboros Worker: Impossible de sauvegarder la file d'attente des alertes Discord: {exc}"
        )


def _load_failed_alerts_queue() -> None:
    global failed_alerts_queue
    if not PENDING_DISCORD_ALERTS_PATH.exists():
        return

    try:
        with PENDING_DISCORD_ALERTS_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            failed_alerts_queue = [item for item in data if isinstance(item, dict)]
        else:
            logger.warning(
                "Ouroboros Worker: Le fichier de file d'attente des alertes Discord est corrompu ou n'est pas une liste."
            )
    except Exception as exc:
        logger.exception(
            f"Ouroboros Worker: Impossible de charger la file d'attente des alertes Discord depuis le fichier: {exc}"
        )


_load_failed_alerts_queue()


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


async def _try_send_discord_alert(title: str, description: str, color: int) -> None:
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
        DISCORD_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    await asyncio.to_thread(urllib.request.urlopen, request)


def _queue_failed_alert(title: str, description: str, color: int) -> None:
    failed_alerts_queue.append(
        {"title": title, "description": description, "color": color}
    )
    _save_failed_alerts_queue()
    logger.warning(
        "Ouroboros Worker: Alerte Discord mise en file d'attente (%d en attente).",
        len(failed_alerts_queue),
    )


async def flush_failed_alerts() -> None:
    if not failed_alerts_queue:
        return

    logger.info(
        "Ouroboros Worker: Tentative de renvoi des alertes Discord en attente (%d).",
        len(failed_alerts_queue),
    )

    while failed_alerts_queue:
        alert = failed_alerts_queue[0]
        try:
            await _try_send_discord_alert(
                alert["title"], alert["description"], alert["color"]
            )
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            logger.warning(
                "Ouroboros Worker: Impossible de renvoyer les alertes Discord en attente, le réseau n'est pas disponible : %s",
                exc,
            )
            break
        except Exception as exc:
            logger.exception(
                f"Ouroboros Worker: Erreur lors du renvoi d'une alerte Discord en attente: {exc}"
            )
            break
        else:
            failed_alerts_queue.pop(0)
            _save_failed_alerts_queue()
            logger.info(
                "Ouroboros Worker: Alerte Discord en attente envoyée et retirée de la file d'attente."
            )


async def send_discord_alert(title: str, description: str, color: int) -> None:
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "REPLACE_ME_NOW":
        logger.info("Ouroboros Worker: Discord webhook URL non configuré ou placeholder détecté.")
        return

    try:
        await _try_send_discord_alert(title, description, color)
        logger.info("Ouroboros Worker: Discord alert envoyé avec succès.")
    except urllib.error.HTTPError as exc:
        logger.exception(
            f"Ouroboros Worker: Discord webhook HTTP error: {exc.code} - {exc.reason}"
        )
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        logger.exception(
            f"Ouroboros Worker: Discord webhook connection error: {exc}"
        )
        _queue_failed_alert(title, description, color)
    except Exception as exc:
        logger.exception(f"Ouroboros Worker: Failed to send Discord alert: {exc}")
        _queue_failed_alert(title, description, color)


async def start_periodic_audit() -> None:
    """Démarre une boucle Ouroboros qui audit les sources toutes les 5 minutes."""
    logger.info("Ouroboros Worker: Démarrage du worker de nuit...")

    orchestrator = LLMOrchestrator(test_mode=False)
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
                        await flush_failed_alerts()
                        await send_discord_alert(
                            title="📜 Sentinelle - Patch autonome appliqué",
                            description="Sentinel a validé et commité automatiquement une amélioration de code. Le déploiement autonome a été réalisé avec succès.",
                            color=65280,
                        )
                    except Exception as exc:
                        logger.exception(
                            f"Ouroboros Worker: Erreur lors de l'envoi de l'alerte Discord de commit: {exc}"
                        )

            if not commit_performed:
                try:
                    await flush_failed_alerts()
                    await send_discord_alert(
                        title="🔎 Sentinelle en veille",
                        description="Système stable, Sentinel veille. Aucun code n'a été modifié lors de ce cycle.",
                        color=255,
                    )
                except Exception as exc:
                    logger.exception(
                        f"Ouroboros Worker: Erreur lors de l'envoi de l'alerte Discord de veille: {exc}"
                    )
        except Exception as exc:
            logger.exception(f"Ouroboros Worker: Erreur durant l'auto-analyse cyclique: {exc}")

        logger.info("Ouroboros Worker: Attente avant la prochaine analyse cyclique de 5 minutes...")
        await asyncio.sleep(300)
