"""🧪 DEMO - Accuracy Coach"""
from src.accuracy.accuracy_coach import AccuracyCoach
from loguru import logger

def main():
    logger.info("\n" + "="*70)
    logger.info("🎓 ACCURACY COACH - LEARNING SYSTEM DEMO")
    logger.info("="*70 + "\n")
    
    coach = AccuracyCoach()
    
    test_executions = [
        {
            "instruction": "Write a Python function for fibonacci",
            "model_used": "claude_code",
            "task_type": "code_implementation",
            "response": "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
            "quality_score": 0.95,
        },
        {
            "instruction": "Explain machine learning",
            "model_used": "mistral",
            "task_type": "explanation",
            "response": "Machine learning is a subset of AI that enables systems to learn from data without explicit programming.",
            "quality_score": 0.88,
        },
        {
            "instruction": "Analyze dataset",
            "model_used": "deepseek",
            "task_type": "data_analysis",
            "response": "The dataset shows correlation between variables X and Y with statistical significance p < 0.05",
            "quality_score": 0.92,
        },
        {
            "instruction": "Debug code",
            "model_used": "mistral",
            "task_type": "code_debugging",
            "response": "The issue is in line 5 where the variable is undefined",
            "quality_score": 0.72,
        },
    ]
    
    logger.info("Processing executions and learning...\n")
    
    for i, execution in enumerate(test_executions, 1):
        logger.info(f"{'='*70}")
        logger.info(f"[Execution {i}] {execution['instruction'][:50]}")
        logger.info(f"{'='*70}")
        
        result = coach.evaluate_execution(execution)
        
        logger.info(f"\nModel used: {execution['model_used']}")
        logger.info(f"Task type: {execution['task_type']}")
        logger.info(f"Quality score: {execution['quality_score']:.0%}")
        logger.info(f"Effectiveness: {result['effectiveness']:.0%}")
        logger.info(f"Was optimal: {result['was_optimal']}")
        logger.info(f"Feedback: {result['feedback']}")
        logger.info(f"Suggestion: {result['suggestion']}")
    
    logger.info(f"\n{'='*70}")
    logger.info("📊 LEARNED RECOMMENDATIONS")
    logger.info(f"{'='*70}\n")
    
    recommendations = coach.get_recommendations()
    logger.info(f"Best model overall: {recommendations['best_model']}")
    logger.info(f"Average effectiveness: {recommendations['best_score']:.0%}")
    logger.info(f"Total executions learned from: {recommendations['total_executions']}\n")
    
    logger.info("Per-model statistics:")
    for model, stats in recommendations['model_stats'].items():
        logger.info(f"  {model}:")
        logger.info(f"    - Executions: {stats['executions']}")
        logger.info(f"    - Avg effectiveness: {stats['average_effectiveness']:.0%}")
    
    logger.info(f"\n{'='*70}")
    logger.info("✅ ACCURACY COACH LEARNING COMPLETE\n")

if __name__ == "__main__":
    main()
