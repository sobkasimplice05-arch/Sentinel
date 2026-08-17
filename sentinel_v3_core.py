import logging
from loguru import logger
from data_collector import DataCollector
from learning_engine import LearningEngine
from memory_manager import SentinelMemory

class SentinelV3Core:
    def __init__(self):
        logger.info("🌐 Initialisation du Noyau Distribué Sentinel v3.0 avec BDD...")
        self.collector = DataCollector()
        self.engine = LearningEngine()
        self.memory = SentinelMemory()

    def run_cycle(self):
        logger.info("⚡ Début du cycle d'évolution autonome...")
        
        # 1. Acquisition des données (Microservice 1)
        raw_data = self.collector.fetch_all()
        
        # 2. Analyse et Intelligence (Microservice 2)
        intelligence_report = self.engine.evaluate_threats(raw_data)
        
        # 3. Enregistrement transactionnel en Base de Données (Microservice 4)
        mutation_id = intelligence_report["mutations_suggested"][0] if intelligence_report["mutations_suggested"] else "no_mutation"
        
        # Sauvegarde ACID sécurisée
        self.memory.save_learning(
            mutation_id=mutation_id,
            success=True,
            learnings_dict=intelligence_report
        )
            
        logger.success("🏁 Cycle Sentinel v3.0 achevé avec succès sur base relationnelle.")

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    sentinel.run_cycle()
