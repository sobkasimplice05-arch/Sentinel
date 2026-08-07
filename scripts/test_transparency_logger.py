"""🧪 DEMO - Transparency Logger"""
from src.logging.transparency_logger import TransparencyLogger
from loguru import logger

def main():
    logger.info("\n" + "="*70)
    logger.info("📊 TRANSPARENCY LOGGER - AUDITABLE EXECUTION DEMO")
    logger.info("="*70 + "\n")
    
    tl = TransparencyLogger()
    
    test_executions = [
        {
            "original_instruction": "Write fibonacci function",
            "cleaned_instruction": "Write fibonacci function",
            "intent": "write_code",
            "language": "python",
            "task_type": "code_implementation",
            "priority_level": "medium",
            "selected_model": "claude_code",
            "model_used": "claude_code",
            "quality_score": 0.95,
            "response": "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
            "effectiveness": 0.95,
            "was_optimal": True,
        },
        {
            "original_instruction": "Explain machine learning",
            "cleaned_instruction": "Explain machine learning",
            "intent": "explain",
            "task_type": "explanation",
            "selected_model": "mistral",
            "model_used": "mistral",
            "quality_score": 0.88,
            "response": "ML is a subset of AI that enables learning from data",
            "effectiveness": 0.88,
            "was_optimal": True,
        },
    ]
    
    logger.info("Logging executions...\n")
    
    for i, execution in enumerate(test_executions, 1):
        logger.info(f"[{i}] Logging: {execution['original_instruction'][:40]}...")
        exec_id = tl.log_execution(execution)
        logger.info(f"    Execution ID: {exec_id}\n")
    
    logger.info("="*70)
    logger.info("📊 EXECUTION SUMMARY")
    logger.info("="*70)
    
    summary = tl.generate_summary()
    logger.info(f"\nTotal executions: {summary['total_executions']}")
    logger.info(f"Average quality: {summary['average_quality_score']:.0%}")
    logger.info(f"\nTask types: {summary['task_types_distribution']}")
    logger.info(f"Models used: {summary['models_used_distribution']}")
    logger.info(f"\nLogs stored in: {summary['logs_directory']}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ TRANSPARENCY LOGGER COMPLETE\n")

if __name__ == "__main__":
    main()
