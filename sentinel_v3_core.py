import logging
from loguru import logger
from data_collector import DataCollector
from learning_engine import LearningEngine
from memory_manager import SentinelMemory
from notifier import SentinelNotifier

class SentinelV3Core:
    def __init__(self):
        logger.info("🌐 Centralisation du Noyau Distribué Sentinel v3.0...")
        self.collector = DataCollector()
        self.engine = LearningEngine()
        self.memory = SentinelMemory()
        self.notifier = SentinelNotifier()

    def run_cycle(self):
        logger.info("⚡ Début du cycle d'évolution autonome rapide...")
        self.notifier.send_alert("Début du cycle d'évolution autonome (Fréquence : 15min).")
        
        raw_data = self.collector.fetch_all()
        intelligence_report = self.engine.evaluate_threats(raw_data)
        mutation_id = str(intelligence_report.get("mutations_suggested", "no_mutation"))
        
        self.memory.save_learning(
            mutation_id=mutation_id,
            success=True,
            learnings_dict=intelligence_report
        )
        
        self.notifier.send_alert(f"Cycle achevé. Score : {intelligence_report['intelligence_score']}%")
        logger.success("🏁 Alignement global Sentinel v3.0 achevé.")

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    sentinel.run_cycle()
