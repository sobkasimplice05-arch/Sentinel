import os
import requests
import logging
from loguru import logger
from datetime import datetime

class SentinelNotifier:
    def __init__(self):
        # Récupération sécurisée du webhook depuis les variables d'environnement
        self.webhook_url = os.getenv("SENTINEL_WEBHOOK_URL", None)
        
        # Configuration d'un fichier journal local en cas de secours
        os.makedirs("logs", exist_ok=True)
        self.local_log_file = "logs/sentinel_mutations.log"

    def send_alert(self, message):
        """Envoie un rapport au Webhook ou l'enregistre localement en cas d'absence de clé"""
        timestamp = datetime.now().isoformat()
        formatted_message = f"[{timestamp}] 🌐 SENTINEL v3.0 : {message}"
        
        if self.webhook_url:
            try:
                payload = {"content": formatted_message}
                response = requests.post(self.webhook_url, json=payload, timeout=5)
                if response.status_code in:
                    logger.success("🔔 Notification distante envoyée avec succès.")
                    return True
            except Exception as e:
                logger.error(f"⚠️ Échec de l'envoi distant ({str(e)}). Bascule sur le rapport local.")
        
        # Fallback : Écriture dans le fichier de logs sécurisé
        try:
            with open(self.local_log_file, "a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")
            logger.info("📝 Rapport d'évolution enregistré dans les journaux locaux.")
        except Exception as e:
            logger.critical(f"❌ Impossible d'écrire le rapport local : {str(e)}")
        return False

if __name__ == "__main__":
    notifier = SentinelNotifier()
    notifier.send_alert("Initialisation du système de notification v3.0 achevée.")
