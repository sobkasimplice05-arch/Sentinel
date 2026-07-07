"""🔤 GRAMMAR CORRECTOR - OUTPUT CLEANING
Corrige la réponse FINALE avant de la donner à l'utilisateur
"""

from typing import Dict
from loguru import logger
from src.quality.grammar_corrector import GrammarCorrectorInput

class GrammarCorrectorOutput:
    """Corrige l'OUTPUT (la réponse finale)"""
    
    def __init__(self):
        logger.info("🔤 Initializing Grammar Corrector Output...")
        self.corrector = GrammarCorrectorInput(language="en")
        logger.info("✅ Grammar Corrector Output ready")
    
    def correct(self, response: str, is_code: bool = False) -> Dict:
        """Corrige une réponse"""
        
        if is_code:
            # Pour du code: ne pas modifier, juste valider
            logger.info("🔤 Code response - validation only")
            return {
                "original": response,
                "corrected": response,
                "is_code": True,
                "changes": 0,
                "confidence": 1.0,
            }
        
        # Pour du texte: correction complète
        logger.info("🔤 Correcting output text...")
        result = self.corrector.correct(response)
        
        return {
            "original": response,
            "corrected": result["corrected"],
            "is_code": False,
            "changes": len(result.get("changes", [])),
            "confidence": result.get("confidence", 0.9),
        }

if __name__ == "__main__":
    corrector = GrammarCorrectorOutput()
    test = "The responce is good"
    result = corrector.correct(test)
    logger.info(f"Original: {result['original']}")
    logger.info(f"Corrected: {result['corrected']}")
