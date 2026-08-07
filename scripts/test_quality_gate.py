"""🧪 DEMO - Quality Gate"""
from src.quality.quality_gate import QualityGate
from loguru import logger

def main():
    logger.info("\n" + "="*70)
    logger.info("🛡️ QUALITY GATE - COMPLETE DEMO")
    logger.info("="*70 + "\n")
    
    gate = QualityGate()
    
    test_cases = [
        {
            "name": "Good Python code",
            "response": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "type": "code_implementation"
        },
        {
            "name": "Response with security issue",
            "response": "password = 'secret123'; eval(user_input)",
            "type": "code_implementation"
        },
        {
            "name": "Complete explanation",
            "response": "Machine learning is a subset of artificial intelligence that enables systems to learn from data without being explicitly programmed.",
            "type": "explanation"
        },
        {
            "name": "Incomplete response",
            "response": "incomplete",
            "type": "code_implementation"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"[{i}] {test['name']}")
        logger.info(f"{'='*70}")
        
        result = gate.evaluate(test['response'], task_type=test['type'])
        
        logger.info(f"\nOverall Score: {result['overall_score']:.0%}")
        logger.info(f"Status: {result['status']}")
        
        logger.info(f"\nChecker Scores:")
        for checker, score_data in result['checkers'].items():
            logger.info(f"  {checker}: {score_data['score']:.0%}")
        
        if result['all_issues']:
            logger.info(f"\nIssues found:")
            for issue in result['all_issues']:
                logger.info(f"  • {issue}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ QUALITY GATE COMPLETE\n")

if __name__ == "__main__":
    main()
