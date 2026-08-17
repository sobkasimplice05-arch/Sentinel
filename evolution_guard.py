import os
import sys
import subprocess
from loguru import logger
from memory_manager import SentinelMemory

class EvolutionGuard:
    def __init__(self):
        self.memory = SentinelMemory()

    def verify_integrity(self):
        """Exécute la suite de tests unitaires pour valider la dernière mutation de code"""
        logger.info("🛡️ EvolutionGuard : Lancement des tests de validation de l'intégrité...")
        try:
            # Exécute pytest de manière isolée
            result = subprocess.run([sys.executable, "-m", "pytest", "tests/"], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.success("✅ Tests validés. La mutation de code est totalement stable.")
                return True
            else:
                logger.critical("🚨 Erreur de régression détectée ! La dernière modification a cassé le système.")
                logger.error(f"Détails de l'erreur :\n{result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Impossible d'exécuter la vérification : {str(e)}")
            return False

    def execute_rollback(self):
        """Annule les modifications récentes de Git en cas d'échec des tests (Auto-Guérison)"""
        logger.warning("🔄 Amorce du protocole d'auto-guérison d'Elliot. Annulation du dernier commit...")
        try:
            # Commande système pour annuler le dernier commit local défectueux
            subprocess.run(["git", "reset", "--hard", "HEAD~1"], check=True)
            logger.success("🛡️ Système restauré avec succès à l'état stable précédent.")
        except Exception as e:
            logger.critical(f"💥 Échec critique du protocole de Rollback : {str(e)}")

if __name__ == "__main__":
    guard = EvolutionGuard()
    # Test de surveillance
    guard.verify_integrity()
