"""
🌐 MULTI-MODEL PARALLEL MUTATIONS
Génère 4 mutations en parallèle via différents modèles
"""
import asyncio
import requests
import json
from loguru import logger

class MultiModelEvolution:
    def __init__(self):
        self.models = {
            "qwen_local": "http://localhost:11434/api/generate",
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "together": "https://api.together.xyz/v1/chat/completions",
            "huggingface": "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf/v1/chat/completions"
        }
    
    async def mutate_via_qwen_local(self, code):
        """Mutation via Qwen local"""
        logger.info("📱 Qwen Local mutation...")
        prompt = f"Améliore ce code en optimisant les boucles:\n{code}"
        try:
            r = requests.post(self.models["qwen_local"], 
                json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False},
                timeout=300)
            return r.json().get("response", "")
        except Exception as e:
            logger.error(f"Qwen failed: {e}")
            return None
    
    async def mutate_via_groq(self, code):
        """Mutation via Groq (Ultra-fast)"""
        logger.info("⚡ Groq mutation...")
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.warning("No Groq API key")
            return None
        
        prompt = f"Améliore ce code en ajoutant du caching:\n{code}"
        try:
            r = requests.post(self.models["groq"],
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "llama-3.1-70b-versatile", "messages": [{"role": "user", "content": prompt}]},
                timeout=60)
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq failed: {e}")
            return None
    
    async def mutate_via_together(self, code):
        """Mutation via Together AI"""
        logger.info("🚀 Together AI mutation...")
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            return None
        
        prompt = f"Améliore ce code en parallelisant:\n{code}"
        try:
            r = requests.post(self.models["together"],
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "mistralai/Mistral-7B-Instruct-v0.1", "messages": [{"role": "user", "content": prompt}]},
                timeout=60)
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Together failed: {e}")
            return None
    
    async def mutate_via_huggingface(self, code):
        """Mutation via Hugging Face"""
        logger.info("🤗 Hugging Face mutation...")
        api_key = os.environ.get("HF_API_KEY")
        if not api_key:
            return None
        
        prompt = f"Améliore ce code en ajoutant des fonctions de détection:\n{code}"
        try:
            r = requests.post(self.models["huggingface"],
                headers={"Authorization": f"Bearer {api_key}"},
                json={"messages": [{"role": "user", "content": prompt}]},
                timeout=120)
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"HF failed: {e}")
            return None
    
    async def generate_4_mutations_parallel(self, code):
        """Génère 4 mutations en PARALLÈLE"""
        logger.info("🔄 Launching 4 parallel mutations...")
        
        mutations = await asyncio.gather(
            self.mutate_via_qwen_local(code),
            self.mutate_via_groq(code),
            self.mutate_via_together(code),
            self.mutate_via_huggingface(code),
            return_exceptions=True
        )
        
        # Filtrer les None et erreurs
        valid_mutations = [m for m in mutations if m and isinstance(m, str)]
        logger.info(f"✅ Got {len(valid_mutations)}/4 valid mutations")
        
        return valid_mutations
    
    def select_best_mutation(self, mutations):
        """Sélectionne la meilleure mutation par taille + complexité"""
        if not mutations:
            return None
        
        # Scoring: plus long + plus complexe = meilleur
        scored = [
            (m, len(m) + m.count("def ") * 50 + m.count("async") * 100)
            for m in mutations
        ]
        best = max(scored, key=lambda x: x[1])
        logger.info(f"🎯 Selected best mutation ({best[1]} complexity score)")
        return best[0]

