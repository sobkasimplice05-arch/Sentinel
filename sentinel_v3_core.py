import json
import logging
from loguru import logger
from data_collector import DataCollector
from learning_engine import LearningEngine
from memory_manager import SentinelMemory

class SentinelV3Core:
    def __init__(self):
        logger.info("🌐 Initialisation du Noyau Distribué Sentinel v3.0...")
        self.collector = DataCollector()
        self.engine = LearningEngine()
        self.memory = SentinelMemory()

    def run_cycle(self):
        """Exécute un cycle complet d'auto-évolution autonome distribuée"""
        logger.info("⚡ Début du cycle d'évolution autonome...")
        
        # 1. Acquisition des données (Microservice 1)
        raw_data = self.collector.fetch_all()
        
        # 2. Analyse et Intelligence (Microservice 2)
        intelligence_report = self.engine.evaluate_threats(raw_data)
        
        # 3. Enregistrement et mise à jour de la Mémoire (Microservice 4)
        try:
            with open(self.memory.filename, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # Injection des nouveaux apprentissages v3.0
            memory_data["metadata"]["last_mutation"] = intelligence_report["timestamp"]
            memory_data["history"].append(intelligence_report)
            
            with open(self.memory.filename, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=4, ensure_ascii=False)
                
            logger.success("💾 Mémoire globale mise à jour et synchronisée avec succès.")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'écriture mémoire : {str(e)}")
            
        logger.success("🏁 Cycle Sentinel v3.0 achevé avec succès.")

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    sentinel.run_cycle()
