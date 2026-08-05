import asyncio
import os
from pathlib import Path
from typing import List

from loguru import logger
from src.orchestrator.llm_orchestrator import LLMOrchestrator
from src.core.self_audit import SelfAudit


async def start_periodic_audit() -> None:
    """Démarre une boucle Ouroboros qui audit les sources toutes les heures."""
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
                if path.is_file() and path.name != "__init__.py"
            ]
            logger.info(f"Ouroboros Worker: {len(source_files)} fichiers sources détectés")

            result = await asyncio.to_thread(self_audit.audit_sources, source_files, True)
            logger.info("Ouroboros Worker: Auto-analyse terminée")
            logger.info(f"Ouroboros Worker: Résultats: {result}")
        except Exception as exc:
            logger.exception(f"Ouroboros Worker: Erreur durant l'auto-analyse cyclique: {exc}")

        logger.info("Ouroboros Worker: Attente avant la prochaine analyse nocturne...")
        await asyncio.sleep(3600)
