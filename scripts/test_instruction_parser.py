"""
🧪 DEMO - Instruction Parser
Test interactif du parser
"""

from src.core.instruction_parser import InstructionParser
from loguru import logger
import json


def main():
    """Main demo"""
    
    logger.info("\n" + "="*70)
    logger.info("🔍 INSTRUCTION PARSER - INTERACTIVE DEMO")
    logger.info("="*70 + "\n")
    
    parser = InstructionParser()
    
    test_cases = [
        "Write a Python function that calculates prime numbers",
        "Debug this JavaScript code that's not working properly",
        "Explain how machine learning algorithms work",
        "Refactor my Django REST API for better performance",
        "Create a React component for user authentication",
        "Write unit tests for my Python module",
        "How do I deploy Docker containers to production?",
        "Build a data analysis script using pandas and numpy",
        "Optimize this SQL query for faster performance",
        "Create a CI/CD pipeline with GitHub Actions",
    ]
    
    logger.info("📝 Parsing instructions:\n")
    
    results_summary = {
        "total": len(test_cases),
        "by_intent": {},
        "by_language": {},
        "by_domain": {},
        "average_confidence": 0,
        "details": []
    }
    
    for i, instruction in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/{len(test_cases)}] '{instruction}'")
        
        result = parser.parse(instruction)
        
        logger.info(f"  Intent:     {result['intent']}")
        logger.info(f"  Language:   {result.get('language', 'N/A')}")
        logger.info(f"  Domain:     {result['domain']}")
        logger.info(f"  Complexity: {result['complexity']}")
        logger.info(f"  Confidence: {result['confidence']:.0%}")
        
        if result.get('requirements'):
            logger.info(f"  Needs:      {', '.join(result['requirements'][:2])}")
        
        # Stats
        intent = result['intent']
        results_summary["by_intent"][intent] = results_summary["by_intent"].get(intent, 0) + 1
        
        language = result.get('language', 'unknown')
        results_summary["by_language"][language] = results_summary["by_language"].get(language, 0) + 1
        
        domain = result['domain']
        results_summary["by_domain"][domain] = results_summary["by_domain"].get(domain, 0) + 1
        
        results_summary["average_confidence"] += result['confidence']
        
        results_summary["details"].append({
            "instruction": instruction,
            "intent": result['intent'],
            "language": result.get('language'),
            "domain": result['domain'],
            "complexity": result['complexity'],
            "confidence": result['confidence']
        })
    
    # Calculate average
    results_summary["average_confidence"] /= len(test_cases)
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("📊 SUMMARY")
    logger.info("="*70)
    logger.info(f"Total: {results_summary['total']} instructions")
    logger.info(f"Average confidence: {results_summary['average_confidence']:.0%}")
    logger.info(f"\nBy Intent:")
    for intent, count in results_summary["by_intent"].items():
        logger.info(f"  {intent}: {count}")
    logger.info(f"\nBy Language:")
    for lang, count in results_summary["by_language"].items():
        if lang != "unknown" and lang != "none":
            logger.info(f"  {lang}: {count}")
    logger.info(f"\nBy Domain:")
    for domain, count in results_summary["by_domain"].items():
        logger.info(f"  {domain}: {count}")
    logger.info("="*70 + "\n")
    
    # Save results
    with open("logs/instruction_parser_demo_results.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    logger.info("✅ Results saved to logs/instruction_parser_demo_results.json\n")


if __name__ == "__main__":
    main()
