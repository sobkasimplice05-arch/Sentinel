import dependency_guardian; dependency_guardian.enforce_dependencies()
import logging
import sqlite3
import random
import subprocess
from loguru import logger
from data_collector import DataCollector
from learning_engine import LearningEngine
from memory_manager import SentinelMemory
from notifier import SentinelNotifier
from ai_matrix import AIMatrix
from evolution_guard import EvolutionGuard
from sentinel_janitor import SentinelJanitor

class SentinelV3Core:
    def __init__(self):
        logger.info("🌐 Centralisation du Noyau Distribué Sentinel v3.0...")
        self.collector = DataCollector()
        self.engine = LearningEngine()
        self.memory = SentinelMemory()
        self.notifier = SentinelNotifier()
        self.ai = AIMatrix()
        self.guard = EvolutionGuard()
        self.janitor = SentinelJanitor()

    def commit_memory(self):
        """CRITICAL: Save memory to git so it survives GitHub Actions purge"""
        try:
            subprocess.run(["git", "config", "user.email", "sentinel-v3@evolution.ai"], check=True)
            subprocess.run(["git", "config", "user.name", "Sentinel-V3-Core"], check=True)
            
            subprocess.run(["git", "add", "sentinel_memory.db", "src/core/circular_memory.json", "sentinel_real_web_discoveries.json"], check=True)
            subprocess.run(["git", "commit", "-m", f"🧬 EVOLUTION: V3 cycle - {logger.info('timestamp')}"], check=False)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
            
            logger.info("✅ MEMORY COMMITTED TO GIT")
            return True
        except Exception as e:
            logger.error(f"❌ COMMIT FAILED: {e}")
            return False

    def run_cycle(self):
        logger.info("⚡ Début du cycle d'évolution autonome rapide...")
        
        try:
            # 1. Maintenance
            self.janitor.purge_old_backups()
            
            # 2. Collecte
            raw_data = self.collector.fetch_all()
            active_sources = ", ".join(raw_data.keys()) if raw_data else "Aucune"
            
            # 3. Analyse et IA
            intelligence_report = self.engine.evaluate_threats(raw_data)
            ai_decision = self.ai.consult_brain(intelligence_report)
            
            intelligence_report["intelligence_score"] = ai_decision["confidence"]
            intelligence_report["ai_source"] = ai_decision["source"]
            intelligence_report["decision_status"] = ai_decision["decision"]
            
            # 4. Écriture BDD SQL
            mutation_id = str(intelligence_report.get("mutations_suggested", "no_mutation"))
            self.memory.save_learning(
                mutation_id=mutation_id,
                success=True,
                learnings_dict=intelligence_report
            )
            
            logger.info(f"✅ Cycle complet: {len(raw_data)} sources, mutation {mutation_id}")
            
            # 5. CRITICAL: COMMIT TO GIT!
            self.commit_memory()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ CYCLE FAILED: {e}")
            return False

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    success = sentinel.run_cycle()
    exit(0 if success else 1)
