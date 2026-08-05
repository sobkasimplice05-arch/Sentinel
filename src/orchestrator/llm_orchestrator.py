"""⚙️ LLM ORCHESTRATOR - Exécution des modèles
Lance les appels aux modèles et gère les erreurs
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os
import time
import requests

from loguru import logger

class LLMOrchestrator:
    """Orchestre l'exécution des modèles LLM"""
    
    def __init__(self, test_mode: bool = False):
        logger.info("⚙️ Initializing LLM Orchestrator...")
        self.max_retries = 3
        self.timeout = 120
        self.test_mode = test_mode or os.getenv("TEST_MODE", "False").lower() == "true"
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset = timedelta(seconds=30)
        self.failure_count = 0
        self.circuit_open_until: Optional[datetime] = None
        logger.info(f"✅ LLM Orchestrator ready (test_mode={self.test_mode})")
    
    def execute(self, routing_result: Dict, instruction: str) -> Dict:
        """Exécute la tâche avec le modèle sélectionné"""
        
        if self._is_circuit_open():
            logger.error("Circuit breaker is open. Skipping model call.")
            return {"success": False, "response": None, "error": "Circuit breaker open", "model_used": None}

        selected_model = routing_result.get("selected_model")
        endpoint = routing_result.get("endpoint", {})
        
        logger.info(f"⚙️ Executing with {selected_model}...")
        logger.info(f"   Instruction: {instruction[:60]}...")
        
        for attempt, model_key in enumerate(["selected_model", "secondary_model", "fallback_model"], start=1):
            model_name = routing_result.get(model_key)
            if not model_name:
                continue
            response = self._call_model(endpoint, instruction, model_name)
            if response is not None:
                self._record_success()
                return {
                    "success": True,
                    "response": response,
                    "model_used": model_name,
                    "attempt": attempt,
                    "fallback_used": attempt != 1,
                }
            logger.warning(f"Model {model_name} failed on attempt {attempt}.")

        self._record_failure()
        return {
            "success": False,
            "response": None,
            "error": "All models failed",
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
            "stream": False,
        }

        for retry in range(self.max_retries):
            try:
                logger.info(f"   Calling {model_name} at {url}/api/generate (attempt {retry + 1})")
                response = requests.post(
                    f"{url}/api/generate",
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                result = response.json()
                if not isinstance(result, dict):
                    logger.error("   ❌ Invalid model response format")
                    continue

                text = result.get("response") or result.get("output") or ""
                if not isinstance(text, str):
                    logger.error("   ❌ Model response missing text field")
                    continue

                text = text.strip()
                if text:
                    logger.info(f"   ✅ Got response ({len(text)} chars)")
                    return text
                logger.warning("   ⚠️ Response empty, retrying")
            except requests.exceptions.Timeout:
                logger.error("   ⏱️ Timeout")
            except requests.exceptions.ConnectionError:
                logger.error("   ❌ Connection error")
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else 'unknown'
                logger.error(f"   ❌ HTTP error {status}: {e}")
            except requests.exceptions.RequestException as e:
                logger.error(f"   ❌ Model request error: {e}")
            except json.JSONDecodeError:
                logger.error("   ❌ Response is not valid JSON")
            except ValueError as e:
                logger.error(f"   ❌ Value error: {e}")

            if retry < self.max_retries - 1:
                wait = min(2 ** retry, 10)
                logger.info(f"   Waiting {wait}s before retry")
                time.sleep(wait)

        return None

    def _is_circuit_open(self) -> bool:
        if self.circuit_open_until is None:
            return False
        if datetime.utcnow() >= self.circuit_open_until:
            self.circuit_open_until = None
            self.failure_count = 0
            return False
        return True

    def _record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.circuit_breaker_threshold:
            self.circuit_open_until = datetime.utcnow() + self.circuit_breaker_reset
            logger.error(f"Circuit breaker opened until {self.circuit_open_until.isoformat()}")

    def _record_success(self) -> None:
        self.failure_count = max(0, self.failure_count - 1)
    
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
