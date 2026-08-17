import os
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentinelMemory:
    def __init__(self, filename="circular_memory.json"):
        self.filename = filename
        self.init_database()

    def init_database(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            initial_structure = {
                "metadata": {
                    "version": "3.0",
                    "created_at": datetime.now().isoformat(),
                    "last_mutation": None
                },
                "history": [],
                "learnings": {}
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(initial_structure, f, indent=4, ensure_ascii=False)
            logging.info("🧬 Noyau Mémoire v3.0 initialisé.")
        else:
            logging.info("💾 Mémoire v3.0 connectée.")

    def backup_memory(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as src:
                data = json.load(src)
            with open(f"{self.filename}.bak", 'w', encoding='utf-8') as dst:
                json.dump(data, dst, indent=4, ensure_ascii=False)
            logging.info("🛡️ Sauvegarde de sécurité créée.")

if __name__ == "__main__":
    memory = SentinelMemory()
