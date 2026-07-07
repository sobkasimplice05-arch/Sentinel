"""🧪 DEMO - Model Router"""
from src.router.model_router import ModelRouter
from loguru import logger

def main():
    logger.info("\n" + "="*70)
    logger.info("🔀 MODEL ROUTER - DEMO")
    logger.info("="*70 + "\n")
    
    router = ModelRouter()
    
    test_tasks = [
        "code_implementation",
        "code_debugging",
        "data_analysis",
        "explanation",
        "system_design",
    ]
    
    logger.info("Testing routing for different task types:\n")
    
    for task in test_tasks:
        logger.info(f"Task: {task}")
        result = router.route({"task_type": task})
        logger.info(f"  Primary: {result['selected_model']}")
        logger.info(f"  Fallback: {result['fallback_model']}\n")
    
    logger.info("="*70)
    logger.info("✅ MODEL ROUTER WORKING\n")

if __name__ == "__main__":
    main()
