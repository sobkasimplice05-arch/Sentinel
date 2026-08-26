import json
import os
import sqlite3
from datetime import datetime, timezone

from loguru import logger


class SentinelMemory:
    def __init__(self, db_filename="sentinel_memory.db"):
        self.db_filename = db_filename
        self.init_database()

    def init_database(self):
        """Crée la base de données relationnelle et la table d'apprentissage v3.0"""
        try:
            conn = sqlite3.connect(self.db_filename)
            cursor = conn.cursor()
            
            # Création de la table selon le schéma d'Elliot
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    mutation_id TEXT,
                    success INTEGER,
                    learnings TEXT,
                    version TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logger.success(f"🧬 Base de données v3.0 SQLite initialisée ({self.db_filename}).")
        except (OSError, sqlite3.Error, TypeError, ValueError) as e:
            logger.error(f"❌ Impossible d'initialiser la base de données : {e!s}")

    def save_learning(self, mutation_id, success, learnings_dict):
        """Enregistre un apprentissage de manière atomique (protection anti-corruption)"""
        try:
            conn = sqlite3.connect(self.db_filename)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_history (timestamp, mutation_id, success, learnings, version)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                mutation_id,
                1 if success else 0,
                json.dumps(learnings_dict),
                "3.0"
            ))
            conn.commit()
            conn.close()
            logger.success("🛡️ Mutation et apprentissage sauvegardés de façon ACID en BDD.")
        except (OSError, sqlite3.Error, TypeError, ValueError) as e:
            logger.error(f"❌ Erreur d'écriture BDD : {e!s}")

    def backup_memory(self):
        """Crée une copie physique de sauvegarde de la base de données"""
        if os.path.exists(self.db_filename):
            import shutil
            shutil.copy2(self.db_filename, f"{self.db_filename}.bak")
            logger.info("💾 Backup physique de la base de données créé (.db.bak).")

if __name__ == "__main__":
    memory = SentinelMemory()
    memory.save_learning("init_v3", True, {"status": "database_active"})
