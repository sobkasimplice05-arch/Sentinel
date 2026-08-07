"""🧪 DEMO - Task Classifier"""
from src.core.instruction_parser import InstructionParser
from src.classifier.task_classifier import TaskClassifier
from loguru import logger

def main():
    logger.info("\n" + "="*70)
    logger.info("📋 TASK CLASSIFIER - COMPLETE PIPELINE DEMO")
    logger.info("="*70 + "\n")
    
    parser = InstructionParser()
    classifier = TaskClassifier()
    
    test_instructions = [
        "Write a Python function for fibonacci",
        "Debug this broken code",
        "Analyze this data with pandas",
        "Explain machine learning",
    ]
    
    logger.info("📝 Complete Pipeline (Parse -> Classify):\n")
    
    for i, instruction in enumerate(test_instructions, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"[{i}] {instruction}")
        logger.info(f"{'='*70}")
        
        parse_result = parser.parse(instruction)
        logger.info(f"Intent: {parse_result['intent']}")
        
        classify_result = classifier.classify(parse_result)
        logger.info(f"Task Type:  {classify_result['task_type']}")
        logger.info(f"Priority:   {classify_result['priority_level']}")
        logger.info(f"Effort:     {classify_result['estimated_effort']}")
        logger.info(f"Model:      {classify_result['routing_hints']['best_model']}")
        logger.info(f"Confidence: {classify_result['confidence']:.0%}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ TASK CLASSIFIER PIPELINE WORKING")
    logger.info("="*70 + "\n")

if __name__ == "__main__":
    main()
