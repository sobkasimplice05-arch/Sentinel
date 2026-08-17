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
        
        # 1. Alerte de début de cycle
        self.notifier.send_alert("Début du cycle d'évolution autonome (Fréquence : 15min).")
        
        # 2. Acquisition et désinfection des données (Microservice 1)
        raw_data = self.collector.fetch_all()
        
        # 3. Analyse et Intelligence (Microservice 2)
        intelligence_report = self.engine.evaluate_threats(raw_data)
        
        # 4. Enregistrement transactionnel en Base de Données (Microservice 4)
        mutation_id = str(intelligence_report.get("mutations_suggested", "no_mutation"))
        
        self.memory.save_learning(
            mutation_id=mutation_id,
            success=True,
            learnings_dict=intelligence_report
        )
        
        # 5. Rapport final de mutation (Microservice Notification)
        self.notifier.send_alert(f"Cycle achevé. Mutations générées avec succès en BDD. Score d'intelligence : {intelligence_report['intelligence_score']}%")
        logger.success("🏁 Alignement global Sentinel v3.0 achevé avec succès.")

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    sentinel.run_cycle()
