import dependency_guardian; dependency_guardian.enforce_dependencies()
import logging
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
        self.notifier.send_alert("Début du cycle d'évolution autonome (Fréquence : 15min).")
        
        self.janitor.purge_old_backups()
        raw_data = self.collector.fetch_all()
        intelligence_report = self.engine.evaluate_threats(raw_data)
        ai_decision = self.ai.consult_brain(intelligence_report)
        
        intelligence_report["intelligence_score"] = ai_decision["confidence"]
        intelligence_report["ai_source"] = ai_decision["source"]
        intelligence_report["decision_status"] = ai_decision["decision"]
        
        mutation_id = str(intelligence_report.get("mutations_suggested", "no_mutation"))
        self.memory.save_learning(
            mutation_id=mutation_id,
            success=True,
            learnings_dict=intelligence_report
        )
        
        if not self.guard.verify_integrity():
            self.notifier.send_alert("🚨 Alerte : Code instable détecté ! Déclenchement du Rollback.")
            self.guard.execute_rollback()
            return
        
        # Formatage de chaîne nettoyé et sécurisé en un seul bloc
        report_msg = f"Cycle complet achevé avec succès par {ai_decision['source']}. Décision : {ai_decision['decision']}. Score : {ai_decision['confidence']}%. Intégrité : OK 🟢"
        self.notifier.send_alert(report_msg)
        logger.success("🏁 Alignement global Sentinel v3.0 achevé avec succès.")

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    sentinel.run_cycle()
