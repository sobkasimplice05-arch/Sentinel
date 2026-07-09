"""⚙️ LLM ORCHESTRATOR - Exécution des modèles
Lance les appels aux modèles et gère les erreurs
"""

from typing import Dict, Optional
from loguru import logger
import requests
import json
import time
import os

class LLMOrchestrator:
    """Orchestre l'exécution des modèles LLM"""
    
    def __init__(self, test_mode: bool = False):
        logger.info("⚙️ Initializing LLM Orchestrator...")
        self.max_retries = 3
        self.timeout = 120
        self.test_mode = test_mode or os.getenv("TEST_MODE", "False").lower() == "true"
        logger.info(f"✅ LLM Orchestrator ready (test_mode={self.test_mode})")
    
    def execute(self, routing_result: Dict, instruction: str) -> Dict:
        """Exécute la tâche avec le modèle sélectionné"""
        
        selected_model = routing_result.get("selected_model")
        endpoint = routing_result.get("endpoint", {})
        
        logger.info(f"⚙️ Executing with {selected_model}...")
        logger.info(f"   Instruction: {instruction[:60]}...")
        
        try:
            # Try primary model
            response = self._call_model(
                endpoint,
                instruction,
                selected_model
            )
            
            if response:
                return {
                    "success": True,
                    "response": response,
                    "model_used": selected_model,
                    "attempt": 1,
                    "fallback_used": False,
                }
            
            # If primary fails, try secondary
            logger.warning(f"Primary model failed, trying secondary...")
            secondary_model = routing_result.get("secondary_model")
            
            response = self._call_model(
                endpoint,
                instruction,
                secondary_model
            )
            
            if response:
                return {
                    "success": True,
                    "response": response,
                    "model_used": secondary_model,
                    "attempt": 2,
                    "fallback_used": True,
                }
            
            # If secondary fails, use fallback
            logger.warning(f"Secondary failed, using fallback...")
            fallback_model = routing_result.get("fallback_model")
            
            response = self._call_model(
                endpoint,
                instruction,
                fallback_model
            )
            
            if response:
                return {
                    "success": True,
                    "response": response,
                    "model_used": fallback_model,
                    "attempt": 3,
                    "fallback_used": True,
                }
            
            return {
                "success": False,
                "response": None,
                "error": "All models failed",
                "model_used": selected_model,
            }
            
        except Exception as e:
            logger.error(f"❌ Orchestration error: {e}")
            return {
                "success": False,
                "response": None,
                "error": str(e),
                "model_used": selected_model,
            }
    
    def _get_mock_response(self, instruction: str, model: str) -> str:
        """Génère une réponse mock pour les tests"""
        mock_responses = {
            "Explain AI": "AI (Artificial Intelligence) is the simulation of human intelligence processes by computer systems. This includes learning, reasoning, and self-correction.",
            "Explain ai": "AI (Artificial Intelligence) is the simulation of human intelligence processes by computer systems. This includes learning, reasoning, and self-correction.",
            "Say hello": "Hello! How can I help you today?",
            "Write hello world": "print('Hello, World!')",
            "Write code": "# Python code example\nprint('Example code')",
            "explain ai": "AI (Artificial Intelligence) is the simulation of human intelligence processes by computer systems. This includes learning, reasoning, and self-correction.",
        }
        
        # Try exact match first
        if instruction in mock_responses:
            return mock_responses[instruction]
        
        # Try case-insensitive match
        for key, value in mock_responses.items():
            if key.lower() == instruction.lower():
                return value
        
        # Default response
        return f"Mock response for: {instruction[:50]}..."
    
    def _call_model(self, endpoint: Dict, instruction: str, model: str) -> Optional[str]:
        """Appelle un modèle spécifique"""
        
        # En mode test, retourner une réponse mock
        if self.test_mode:
            logger.info(f"   Calling {model}... (TEST MODE)")
            response = self._get_mock_response(instruction, model)
            logger.info(f"   ✅ Got mock response ({len(response)} chars)")
            return response
        
        url = endpoint.get("url", "http://localhost:11434")
        model_name = endpoint.get("model_name", model)
        max_tokens = endpoint.get("max_tokens", 2000)
        
        payload = {
            "model": model_name,
            "prompt": instruction,
            "temperature": 0.3,
            "num_predict": max_tokens,
            "stream": False
        }
        
        try:
            logger.info(f"   Calling {model}...")
            
            response = requests.post(
                f"{url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                
                if text:
                    logger.info(f"   ✅ Got response ({len(text)} chars)")
                    return text
            else:
                logger.error(f"   ❌ Status {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            logger.error(f"   ⏱️ Timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"   ❌ Connection error")
            return None
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            return None
    
    def batch_execute(self, routing_results: list, instructions: list) -> list:
        """Exécute plusieurs tâches"""
        
        logger.info(f"⚙️ Batch executing {len(instructions)} tasks...")
        results = []
        
        for i, (routing, instruction) in enumerate(zip(routing_results, instructions)):
            logger.info(f"   [{i+1}/{len(instructions)}]")
            result = self.execute(routing, instruction)
            results.append(result)
        
        logger.info("✅ Batch execution complete")
        return results

def demo():
    logger.info("\n" + "="*70)
    logger.info("⚙️ LLM ORCHESTRATOR - DEMO")
    logger.info("="*70 + "\n")
    
    from src.router.model_router import ModelRouter
    
    router = ModelRouter()
    orchestrator = LLMOrchestrator()
    
    test_tasks = [
        {"task_type": "explanation", "instruction": "What is Python?"},
        {"task_type": "code_implementation", "instruction": "Write hello world"},
    ]
    
    for task in test_tasks:
        logger.info(f"\n[Task] {task['task_type']}")
        
        routing = router.route(task)
        logger.info(f"Model: {routing['selected_model']}")
        
        # Note: This will fail without Ollama running
        # result = orchestrator.execute(routing, task['instruction'])
    
    logger.info("\n" + "="*70)
    logger.info("✅ ORCHESTRATOR READY\n")

if __name__ == "__main__":
    demo()
