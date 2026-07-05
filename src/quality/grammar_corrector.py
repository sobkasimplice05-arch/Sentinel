"""
🛡️ SENTINEL - QUALITY GATE
Module de correction grammaticale automatique des entrées utilisateur.
"""

import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from loguru import logger

# Supprime l'avertissement Windows sur les liens symboliques pour la portabilité
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

class GrammarCorrectorInput:
    """
    Système de nettoyage et de correction de la syntaxe avant traitement par l'orchestateur.
    Utilise le modèle Seq2Seq CoEdit de Grammarly.
    """
    
    def __init__(self, language: str = "en"):
        self.language = language.lower()
        self.model_name = "grammarly/coedit-large"
        
        # Sélection du processeur (GPU ou CPU)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"⚙️ Loading Grammar Corrector on device: {self.device}")
        
        # Chargement local
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
        logger.info("🛡️ Grammar Corrector core engine loaded successfully.")

    def correct(self, text: str) -> dict:
        """
        Corrige une chaîne de caractères et retourne un dictionnaire complet de métadonnées.
        """
        if not text or text.strip() == "":
            return {
                "original": "",
                "corrected": "",
                "changes": [],
                "change_count": 0,
                "confidence": 1.0,
                "device": self.device,
                "should_process": False
            }
            
        text_normalized = " ".join(text.split())
        prompt = f"Fix grammatical errors: {text_normalized}"
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs, 
                    max_length=256,
                    num_beams=4,
                    early_stopping=True
                )
            corrected_text = self.tokenizer.decode(outputs, skip_special_tokens=True)
            if corrected_text:
                # Force la première lettre en majuscule
                corrected_text = corrected_text[0].upper() + corrected_text[1:]
                
        except Exception as e:
            logger.error(f"❌ Error during model execution: {str(e)}")
            corrected_text = text_normalized

        changes = []
        if text_normalized.lower() != corrected_text.lower():
            changes.append({
                "from": text_normalized,
                "to": corrected_text,
                "type": "GRAMMAR_FIX"
            })
            confidence_score = 0.88
        else:
            confidence_score = 0.98

        return {
            "original": text,
            "corrected": corrected_text,
            "changes": changes,
            "change_count": len(changes),
            "confidence": confidence_score,
            "device": self.device,
            "should_process": len(changes) > 0
        }

    def batch_correct(self, texts: list) -> list:
        return [self.correct(t) for t in texts]
