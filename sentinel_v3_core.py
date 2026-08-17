import dependency_guardian; dependency_guardian.enforce_dependencies()
import logging
from loguru import logger
from data_collector import DataCollector
from learning_engine import LearningEngine
from memory_manager import SentinelMemory
from notifier import SentinelNotifier
from ai_matrix import AIMatrix

class SentinelV3Core:
    def __init__(self):
        logger.info("🌐 Centralisation du Noyau Distribué Sentinel v3.0...")
        self.collector = DataCollector()
        self.engine = LearningEngine()
        self.memory = SentinelMemory()
        self.notifier = SentinelNotifier()
        self.ai = AIMatrix()

    def run_cycle(self):
        logger.info("⚡ Début du cycle d'évolution autonome rapide...")
        self.notifier.send_alert("Début du cycle d'évolution autonome (Fréquence : 15min).")
        
        # 1. Acquisition et désinfection des données
        raw_data = self.collector.fetch_all()
        
        # 2. Analyse initiale des patterns
        intelligence_report = self.engine.evaluate_threats(raw_data)
        
        # 3. Consultation du Cerveau Multi-LLM (Ajout Commande 13)
        ai_decision = self.ai.consult_brain(intelligence_report)
        
        # Enrichissement du rapport avec la décision de l'IA
        intelligence_report["intelligence_score"] = ai_decision["confidence"]
        intelligence_report["ai_source"] = ai_decision["source"]
        intelligence_report["decision_status"] = ai_decision["decision"]
        
        # 4. Enregistrement transactionnel en Base de Données SQL ACID
        mutation_id = str(intelligence_report.get("mutations_suggested", "no_mutation"))
        self.memory.save_learning(
            mutation_id=mutation_id,
            success=True,
            learnings_dict=intelligence_report
        )
        
        # 5. Rapport final de mutation
        self.notifier.send_alert(
            f"Cycle achevé par {ai_decision['source']}. "
            f"Décision : {ai_decision['decision']}. "
            f"Score d'intelligence : {ai_decision['confidence']}%"
        )
        logger.success("🏁 Alignement global Sentinel v3.0 achevé avec succès.")

if __name__ == "__main__":
    sentinel = SentinelV3Core()
    sentinel.run_cycle()
