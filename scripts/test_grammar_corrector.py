"""
🧪 MANUAL TEST SCRIPT - Grammar Corrector
À exécuter pour voir le correcteur en action
"""

from src.quality.grammar_corrector import GrammarCorrectorInput
from loguru import logger
import json

def main():
    logger.info("\n" + "="*70)
    logger.info("🛡️ GRAMMAR CORRECTOR - MANUAL TEST")
    logger.info("="*70 + "\n")
    
    logger.info("📥 Initializing Grammar Corrector...")
    corrector = GrammarCorrectorInput(language="en")
    logger.info("✅ Initialized\n")
    
    test_inputs = [
        "hello world",
        "i am a programmer",
        "he dont like coding",
        "there is many bugs in the code",
        "she go to the store yesterday",
        "the quick brown fox jumps over the lazy dog",
        "machine learning is a branch of artificial inteligence",
        "python is a powerfull language for data science",
        "we has three cats and two dogs",
    ]
    
    logger.info("📝 Testing corrections:\n")
    
    results_summary = {
        "total": len(test_inputs),
        "average_confidence": 0,
        "total_changes": 0,
        "details": []
    }
    
    for i, input_text in enumerate(test_inputs, 1):
        logger.info(f"\n[Test {i}/{len(test_inputs)}]")
        logger.info(f"  Original:  '{input_text}'")
        
        result = corrector.correct(input_text)
        
        logger.info(f"  Corrected: '{result['corrected']}'")
        logger.info(f"  Confidence: {result['confidence']:.0%}")
        logger.info(f"  Changes: {result['change_count']}")
        
        if result['changes']:
            logger.info(f"  Change details:")
            for j, change in enumerate(result['changes'][:5], 1):
                logger.info(f"    {j}. {change.get('from', 'INSERT')} → {change.get('to', 'DELETE')} ({change.get('type')})")
        else:
            logger.info(f"  No changes needed")
        
        results_summary["details"].append({
            "input": input_text,
            "output": result['corrected'],
            "confidence": result['confidence'],
            "changes": result['change_count']
        })
        
        results_summary["average_confidence"] += result['confidence']
        results_summary["total_changes"] += result['change_count']
    
    results_summary["average_confidence"] /= len(test_inputs)
    
    logger.info("\n" + "="*70)
    logger.info("📊 SUMMARY")
    logger.info("="*70)
    logger.info(f"Total tests: {results_summary['total']}")
    logger.info(f"Average confidence: {results_summary['average_confidence']:.0%}")
    logger.info(f"Total changes made: {results_summary['total_changes']}")
    logger.info("="*70 + "\n")
    
    with open("logs/grammar_corrector_test_results.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    logger.info("✅ Results saved to logs/grammar_corrector_test_results.json\n")

if __name__ == "__main__":
    main()
