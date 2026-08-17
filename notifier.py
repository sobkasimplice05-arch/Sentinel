import os
import requests
from loguru import logger
from datetime import datetime

class SentinelNotifier:
          def __init__(self):
                    self.webhook_url = "https://discord.com/api/webhooks/1538912523502489683/20VmZHXY5Ipg0NQpLPblF2AqrET8D2VGzRXN3ACLoLp5snnQDMUUxgj64lckedWO7iAA"
                    os.makedirs("logs", exist_ok=True)
                    self.local_log_file = "logs/sentinel_mutations.log"

          def send_alert(self, message):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    formatted_message = f" **SENTINEL v3.0** [{timestamp}]\n{message}"
                    
                    if self.webhook_url and "discord.com" in self.webhook_url:
                              try:
                                        payload = {"content": formatted_message}
                                        response = requests.post(self.webhook_url, json=payload, timeout=5)
                                        if 200 <= response.status_code < 300:
                                                  logger.success(" Notification push envoyée sur Discord !")
                                                  return True
                              except Exception as e:
                                        logger.error(f" Échec de l'envoi Discord : {str(e)}")
                    
                    with open(self.local_log_file, "a", encoding="utf-8") as f:
                              f.write(f"[{timestamp}] {message}\n")
                    return False

if __name__ == "__main__":
          notifier = SentinelNotifier()
          notifier.send_alert(" Liaison mobile Discord opérationnelle !")
