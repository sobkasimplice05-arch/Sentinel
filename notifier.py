import os
import requests
from loguru import logger
from datetime import datetime

class SentinelNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("SENTINEL_WEBHOOK_URL", None)
        os.makedirs("logs", exist_ok=True)
        self.local_log_file = "logs/sentinel_mutations.log"

    def send_alert(self, message):
        timestamp = datetime.now().isoformat()
        formatted_message = f"[{timestamp}] 🌐 SENTINEL v3.0 : {message}"
        
        if self.webhook_url:
            try:
                payload = {"content": formatted_message}
                response = requests.post(self.webhook_url, json=payload, timeout=5)
                # Correction de la syntaxe : vérification des codes de succès HTTP (200-299)
                if 200 <= response.status_code < 300:
                    logger.success("🔔 Notification distante envoyée.")
                    return True
            except Exception as e:
                logger.error(f"⚠️ Échec notif distante ({str(e)}).")
        
        try:
            with open(self.local_log_file, "a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")
            logger.info("📝 Rapport enregistré localement.")
        except Exception as e:
            logger.critical(f"❌ Erreur écriture log : {str(e)}")
        return False

if __name__ == "__main__":
    notifier = SentinelNotifier()
    notifier.send_alert("Test de stabilité v3.0 après correction syntaxique.")
