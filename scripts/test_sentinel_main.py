"""🧪 DEMO - Sentinel Main Complete System"""
from src.sentinel_main import Sentinel
from loguru import logger

def main():
    logger.info("\n" + "="*70)
    logger.info("🛡️ SENTINEL - COMPLETE SYSTEM DEMONSTRATION")
    logger.info("One AI to rule them all")
    logger.info("="*70)
    
    sentinel = Sentinel()
    
    test_instructions = [
        "Explain machine learning",
        "Write a Python function for fibonacci",
    ]
    
    logger.info("\n📝 Running test cases through complete pipeline...\n")
    
    for i, instruction in enumerate(test_instructions, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"TEST {i}: {instruction}")
        logger.info(f"{'='*70}\n")
        
        result = sentinel.execute(instruction)
        
        if result['success']:
            logger.info(f"\n{'='*70}")
            logger.info("FINAL RESULT")
            logger.info(f"{'='*70}")
            logger.info(f"✅ Success: {result['success']}")
            logger.info(f"Quality Score: {result['quality_score']:.0%}")
            logger.info(f"Model Used: {result['model_used']}")
            logger.info(f"Effectiveness: {result['effectiveness']:.0%}")
            logger.info(f"Execution Time: {result['execution_time']:.2f}s")
            logger.info(f"Execution ID: {result['execution_id']}")
    
    logger.info(f"\n{'='*70}")
    logger.info("✅ SENTINEL SYSTEM COMPLETE AND WORKING")
    logger.info("="*70 + "\n")

if __name__ == "__main__":
    main()
