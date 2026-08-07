"""🧪 DEMO - LLM Orchestrator"""
from src.orchestrator.llm_orchestrator import LLMOrchestrator
from src.router.model_router import ModelRouter
from loguru import logger

def main():
    logger.info("\n" + "="*70)
    logger.info("⚙️ LLM ORCHESTRATOR - DEMO")
    logger.info("="*70 + "\n")
    
    router = ModelRouter()
    orchestrator = LLMOrchestrator()
    
    logger.info("Pipeline flow:\n")
    
    test_tasks = [
        {"task_type": "explanation", "instruction": "What is machine learning?"},
        {"task_type": "code_implementation", "instruction": "Write fizzbuzz"},
    ]
    
    for i, task in enumerate(test_tasks, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"[{i}] Task: {task['task_type']}")
        logger.info(f"{'='*70}")
        
        routing = router.route(task)
        logger.info(f"Model selected: {routing['selected_model']}")
        
        result = orchestrator.execute(routing, task['instruction'])
        
        if result['success']:
            logger.info(f"✅ Execution successful")
            logger.info(f"Response (first 100 chars): {result.get('response', '')[:100]}")
        else:
            logger.info(f"⚠️ Execution needs Ollama running")
    
    logger.info("\n" + "="*70)
    logger.info("✅ ORCHESTRATOR PIPELINE COMPLETE\n")

if __name__ == "__main__":
    main()
