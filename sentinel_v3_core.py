import dependency_guardian; dependency_guardian.enforce_dependencies()
import logging
import sqlite3
import random
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

    def run_cycle(self):
        logger.info("⚡ Début du cycle d'évolution autonome rapide...")
        
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
        
        # 5. Récupération du nombre total de lignes en BDD pour dynamiser le message
        try:
            conn = sqlite3.connect(self.memory.db_filename)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM learning_history")
            total_cycles = cursor.fetchone()[0]
            conn.close()
        except Exception:
            total_cycles = "Inconnu"
            
        # 6. Bouclier Anti-Crash
        if not self.guard.verify_integrity():
            self.notifier.send_alert("🚨 **Alerte : Code instable détecté !** Déclenchement immédiat du protocole de Rollback.")
            self.guard.execute_rollback()
            return
        
        # 7. Générateur de rapports dynamiques (Phrases aléatoires)
        intros = [
            "L'esprit cyber de Sentinel continue de s'étendre.",
            "Analyse réseau complétée avec succès.",
            "Le protocole Ouroboros a consolidé le code source."
        ]
        intro_text = random.choice(intros)
        
        report_msg = (
            f"📈 **Rapport d'Évolution Dynamique**\n"
            f"✨ {intro_text}\n"
            f"📡 _Sources synchronisées_ : `{active_sources}`\n"
            f"🧠 _Moteur actif_ : `{ai_decision['source']}`\n"
            f"📊 _Index de mémoire global_ : `{total_cycles} cycles stockés`\n"
            f"🛡️ _Intégrité logicielle_ : `OK - 100% Stable 🟢`"
        )
        
        self.notifier.send_alert(report_msg)
        logger.success("🏁 Alignement global Sentinel v3.0 achevé avec succès.")

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    sentinel.run_cycle()
