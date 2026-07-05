"""
🔄 INPUT PIPELINE
Utilise Grammar Corrector comme première étape du pipeline
"""

from src.quality.grammar_corrector import GrammarCorrectorInput
from loguru import logger
from typing import Dict


class InputPipeline:
    """
    Pipeline d'input Sentinel
    
    Étapes:
    1. Grammar Correction (nettoyage)
    2. Parsing (extraction info)
    3. Classification (type de tâche)
    """
    
    def __init__(self, language: str = "en"):
        """Initialise le pipeline"""
        
        logger.info("🔄 Initializing Input Pipeline...")
        
        self.grammar_corrector = GrammarCorrectorInput(language=language)
        self.language = language
        
        logger.info("✅ Input Pipeline ready")
    
    def process(self, user_input: str) -> Dict:
        """
        Traite l'input utilisateur
        
        Args:
            user_input: Input brut de l'utilisateur
        
        Returns:
            Dict avec input nettoyé et metadata
        """
        
        logger.info(f"🔄 Processing user input...")
        
        # Step 1: Grammar Correction
        logger.info("  Step 1: Grammar Correction...")
        grammar_result = self.grammar_corrector.correct(user_input)
        
        cleaned_input = grammar_result["corrected"]
        confidence = grammar_result["confidence"]
        
        logger.info(f"  ✅ Grammar check complete (confidence: {confidence:.0%})")
        
        # Step 2: Basic validation
        if not cleaned_input.strip():
            logger.error("❌ Empty input after correction")
            return {
                "success": False,
                "error": "Empty input"
            }
        
        # Step 3: Return result
        result = {
            "success": True,
            "original": user_input,
            "cleaned": cleaned_input,
            "grammar_confidence": confidence,
            "grammar_changes": grammar_result["change_count"],
            "ready_for_processing": grammar_result["should_process"],
        }
        
        logger.info("✅ Input processing complete")
        
        return result


# Demo
if __name__ == "__main__":
    logger.info("\n" + "="*70)
    logger.info("🧪 INPUT PIPELINE DEMO")
    logger.info("="*70 + "\n")
    
    pipeline = InputPipeline(language="en")
    
    test_inputs = [
        "hello",
        "can you write a python function",
        "he dont like coding",
    ]
    
    for test in test_inputs:
        logger.info(f"\n📥 Input: '{test}'")
        result = pipeline.process(test)
        logger.info(f"📤 Output: '{result['cleaned']}'")
        logger.info(f"✅ Ready: {result['ready_for_processing']}")
