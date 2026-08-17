import os
import time
from loguru import logger

class SentinelJanitor:
    def __init__(self):
        self.target_extensions = [".bak", ".log.bak"]
        self.max_age_seconds = 86400  # 24 heures en secondes

    def purge_old_backups(self):
        """Scanne le dépôt et supprime les fichiers temporaires obsolètes"""
        logger.info("🧼 Janitor : Lancement du nettoyage des fichiers temporaires...")
        current_time = time.time()
        deleted_count = 0

        for root, dirs, files in os.walk("."):
            for file in files:
                if any(file.endswith(ext) for ext in self.target_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        # Vérification de l'âge du fichier
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > self.max_age_seconds:
                            os.remove(file_path)
                            logger.success(f"🗑️ Fichier obsolète supprimé : {file}")
                            deleted_count += 1
                    except Exception as e:
                        logger.error(f"⚠️ Impossible de nettoyer {file} : {str(e)}")

        logger.info(f"✨ Maintenance achevée. Fichiers purgés : {deleted_count}")
        return deleted_count

if __name__ == "__main__":
    janitor = SentinelJanitor()
    janitor.purge_old_backups()
