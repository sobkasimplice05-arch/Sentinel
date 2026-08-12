"""
📤 DISCORD WEBHOOK - Send real mutation reports
"""
import os
import requests
import json
from loguru import logger
from src.core.mutation_reporter import MutationReporter

class DiscordWebhook:
    def __init__(self):
        self.webhook_url = os.environ.get("SENTINEL_DISCORD_WEBHOOK")
        self.reporter = MutationReporter()
    
    def send_mutation_report(self, cycle_num, mutation_data):
        """Envoie un rapport UNIQUE à Discord"""
        
        if not self.webhook_url:
            logger.warning("⚠️ No Discord webhook configured")
            return False
        
        try:
            # Génère rapport unique
            report = self.reporter.generate_report(cycle_num, mutation_data)
            
            # Formate pour Discord
            message = self.reporter.format_for_discord(report)
            
            # Envoie à Discord
            payload = {
                "content": message,
                "username": "Sentinel Ouroboros",
                "avatar_url": "https://i.imgur.com/4O0Oqgf.png"  # IA emoji
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Mutation #{cycle_num} reported to Discord")
                return True
            else:
                logger.error(f"❌ Discord webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Discord error: {e}")
            return False
    
    def send_error_report(self, cycle_num, error_msg, error_type):
        """Envoie un rapport d'ERREUR à Discord"""
        
        if not self.webhook_url:
            return False
        
        try:
            message = f"""
🔴 **SENTINEL ERROR REPORT**

**Cycle:** #{cycle_num}
**Error Type:** {error_type}
**Message:** {error_msg}

Status: ⚠️ FAILED
"""
            
            payload = {
                "content": message,
                "username": "Sentinel Ouroboros",
                "avatar_url": "https://i.imgur.com/4O0Oqgf.png"
            }
            
            requests.post(self.webhook_url, json=payload, timeout=10)
            return True
            
        except Exception as e:
            logger.error(f"Discord error report failed: {e}")
            return False

