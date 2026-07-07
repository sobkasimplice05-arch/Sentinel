"""🎓 ACCURACY COACH - Système de feedback et optimisation
Mesure la performance et optimise le routing
"""

from typing import Dict, List
from loguru import logger
from datetime import datetime
import json

class AccuracyCoach:
    """Le coach qui mesure et optimise"""
    
    def __init__(self):
        logger.info("🎓 Initializing Accuracy Coach...")
        self.execution_history = []
        self.model_scores = {}
        self.routing_effectiveness = {}
        logger.info("✅ Accuracy Coach ready")
    
    def evaluate_execution(self, execution_data: Dict) -> Dict:
        """Évalue une exécution complète"""
        
        logger.info("🎓 Evaluating execution...")
        
        instruction = execution_data.get("instruction", "")
        model_used = execution_data.get("model_used", "unknown")
        response = execution_data.get("response", "")
        quality_score = execution_data.get("quality_score", 0.5)
        task_type = execution_data.get("task_type", "unknown")
        
        # Calculate effectiveness
        effectiveness = self._calculate_effectiveness(
            model_used,
            task_type,
            quality_score,
            response
        )
        
        # Check if best model was used
        was_optimal = self._check_optimal_routing(model_used, task_type, effectiveness)
        
        # Generate feedback
        feedback = self._generate_feedback(
            model_used,
            task_type,
            effectiveness,
            was_optimal
        )
        
        # Store in history
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction[:100],
            "model_used": model_used,
            "task_type": task_type,
            "quality_score": quality_score,
            "effectiveness": effectiveness,
            "was_optimal": was_optimal,
            "feedback": feedback,
        }
        
        self.execution_history.append(execution_record)
        self._update_scores(model_used, task_type, effectiveness)
        
        logger.info(f"✅ Evaluation complete")
        logger.info(f"   Effectiveness: {effectiveness:.0%}")
        logger.info(f"   Was optimal: {was_optimal}")
        
        return {
            "effectiveness": effectiveness,
            "was_optimal": was_optimal,
            "feedback": feedback,
            "suggestion": self._get_suggestion(model_used, task_type, effectiveness),
        }
    
    def _calculate_effectiveness(self, model: str, task_type: str, quality_score: float, response: str) -> float:
        """Calcule l'efficacité (0-1)"""
        
        base_score = quality_score * 0.7  # 70% weight to quality
        
        # Add bonus for response length
        length_bonus = min(0.2, len(response) / 1000)  # Max 20% bonus
        
        # Penalty for common issues
        penalty = 0
        if "error" in response.lower():
            penalty += 0.1
        if "not implemented" in response.lower():
            penalty += 0.15
        
        effectiveness = base_score + length_bonus - penalty
        return max(0, min(1, effectiveness))
    
    def _check_optimal_routing(self, model: str, task_type: str, effectiveness: float) -> bool:
        """Vérifie si c'était le meilleur modèle"""
        
        optimal_models = {
            "code_implementation": "claude_code",
            "code_debugging": "claude_code",
            "data_analysis": "deepseek",
            "explanation": "mistral",
            "system_design": "claude_code",
        }
        
        optimal = optimal_models.get(task_type, "mistral")
        
        # C'est optimal si c'est le bon modèle ET efficacité > 0.75
        return model == optimal and effectiveness >= 0.75
    
    def _generate_feedback(self, model: str, task_type: str, effectiveness: float, was_optimal: bool) -> str:
        """Génère du feedback"""
        
        if was_optimal:
            return f"Great! {model} was the right choice for {task_type} (effectiveness: {effectiveness:.0%})"
        
        if effectiveness >= 0.8:
            return f"{model} worked well, but there might be a better option for {task_type}"
        
        if effectiveness >= 0.6:
            return f"{model} was acceptable, consider trying a different model next time"
        
        return f"Consider using a different model for {task_type} next time (effectiveness was low)"
    
    def _get_suggestion(self, model: str, task_type: str, effectiveness: float) -> str:
        """Suggestion pour la prochaine fois"""
        
        suggestions = {
            "code_implementation": "Use claude_code for better code generation",
            "code_debugging": "Use claude_code for debugging",
            "data_analysis": "Use deepseek for better reasoning",
            "explanation": "Use mistral for clearer explanations",
            "system_design": "Use claude_code for architecture",
        }
        
        return suggestions.get(task_type, "No suggestion available")
    
    def _update_scores(self, model: str, task_type: str, effectiveness: float):
        """Met à jour les scores du modèle"""
        
        if model not in self.model_scores:
            self.model_scores[model] = {"total": 0, "sum": 0, "count": 0}
        
        self.model_scores[model]["count"] += 1
        self.model_scores[model]["sum"] += effectiveness
        self.model_scores[model]["total"] = self.model_scores[model]["sum"] / self.model_scores[model]["count"]
    
    def get_model_stats(self, model: str = None) -> Dict:
        """Retourne les stats des modèles"""
        
        if model:
            stats = self.model_scores.get(model, {})
            return {
                "model": model,
                "executions": stats.get("count", 0),
                "average_effectiveness": round(stats.get("total", 0), 2),
            }
        
        all_stats = {}
        for m, stats in self.model_scores.items():
            all_stats[m] = {
                "executions": stats["count"],
                "average_effectiveness": round(stats["total"], 2),
            }
        
        return all_stats
    
    def get_recommendations(self) -> Dict:
        """Recommandations basées sur l'historique"""
        
        logger.info("🎓 Generating recommendations...")
        
        if not self.execution_history:
            return {"message": "No execution history yet"}
        
        stats = self.get_model_stats()
        
        # Meilleur modèle
        best_model = max(stats, key=lambda x: stats[x]["average_effectiveness"])
        best_score = stats[best_model]["average_effectiveness"]
        
        return {
            "best_model": best_model,
            "best_score": best_score,
            "total_executions": len(self.execution_history),
            "model_stats": stats,
            "suggestion": f"Focus on using {best_model} for better results",
        }

def demo():
    logger.info("\n" + "="*70)
    logger.info("🎓 ACCURACY COACH - DEMO")
    logger.info("="*70 + "\n")
    
    coach = AccuracyCoach()
    
    test_executions = [
        {
            "instruction": "Write fibonacci function",
            "model_used": "claude_code",
            "task_type": "code_implementation",
            "response": "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
            "quality_score": 0.9,
        },
        {
            "instruction": "Explain ML",
            "model_used": "mistral",
            "task_type": "explanation",
            "response": "Machine learning is a subset of AI...",
            "quality_score": 0.85,
        },
        {
            "instruction": "Analyze data",
            "model_used": "deepseek",
            "task_type": "data_analysis",
            "response": "The data shows a trend of...",
            "quality_score": 0.88,
        },
    ]
    
    for i, execution in enumerate(test_executions, 1):
        logger.info(f"\n[Execution {i}]")
        result = coach.evaluate_execution(execution)
        logger.info(f"Effectiveness: {result['effectiveness']:.0%}")
        logger.info(f"Was optimal: {result['was_optimal']}")
        logger.info(f"Feedback: {result['feedback']}")
    
    logger.info(f"\n{'='*70}")
    logger.info("📊 Recommendations:")
    logger.info(f"{'='*70}")
    
    recommendations = coach.get_recommendations()
    logger.info(f"Best model: {recommendations['best_model']}")
    logger.info(f"Average score: {recommendations['best_score']:.0%}")
    logger.info(f"Total executions: {recommendations['total_executions']}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ ACCURACY COACH WORKING\n")

if __name__ == "__main__":
    demo()
