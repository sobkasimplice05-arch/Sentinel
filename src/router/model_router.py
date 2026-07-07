"""🔀 MODEL ROUTER - LE GÉNÉRAL
Orchestre multi-IA avec local-first strategy
"""

from typing import Dict, List
from loguru import logger
from enum import Enum

class Model(str, Enum):
    CLAUDE_CODE = "claude_code"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    PHI = "phi"
    QWEN = "qwen"
    UNKNOWN = "unknown"

class ModelProvider(str, Enum):
    OLLAMA_LOCAL = "ollama_local"
    CLAUDE_API = "claude_api"
    UNKNOWN = "unknown"

ROUTING_RULES = {
    "code_implementation": {
        "primary": Model.CLAUDE_CODE,
        "secondary": Model.QWEN,
        "fallback": Model.MISTRAL,
    },
    "code_debugging": {
        "primary": Model.CLAUDE_CODE,
        "secondary": Model.DEEPSEEK,
        "fallback": Model.MISTRAL,
    },
    "algorithm_implementation": {
        "primary": Model.CLAUDE_CODE,
        "secondary": Model.DEEPSEEK,
        "fallback": Model.QWEN,
    },
    "data_analysis": {
        "primary": Model.DEEPSEEK,
        "secondary": Model.QWEN,
        "fallback": Model.MISTRAL,
    },
    "explanation": {
        "primary": Model.MISTRAL,
        "secondary": Model.CLAUDE_CODE,
        "fallback": Model.PHI,
    },
    "system_design": {
        "primary": Model.CLAUDE_CODE,
        "secondary": Model.DEEPSEEK,
        "fallback": Model.QWEN,
    },
}

MODEL_ENDPOINTS = {
    Model.MISTRAL: {
        "name": "Mistral 7B",
        "provider": "ollama_local",
        "url": "http://localhost:11434",
        "model_name": "mistral",
        "max_tokens": 2000,
    },
    Model.QWEN: {
        "name": "Qwen 2.5-Coder 7B",
        "provider": "ollama_local",
        "url": "http://localhost:11434",
        "model_name": "qwen2.5-coder:7b",
        "max_tokens": 3000,
    },
    Model.PHI: {
        "name": "Phi 2.7B",
        "provider": "ollama_local",
        "url": "http://localhost:11434",
        "model_name": "phi",
        "max_tokens": 1000,
    },
    Model.CLAUDE_CODE: {
        "name": "Claude Code (via Ollama)",
        "provider": "ollama_local",
        "url": "http://localhost:11434",
        "model_name": "mistral",
        "max_tokens": 4096,
    },
}

class ModelRouter:
    """Le GÉNÉRAL qui orchestre tous les modèles"""
    
    def __init__(self):
        logger.info("🔀 Initializing Model Router...")
        self.routing_rules = ROUTING_RULES
        self.model_endpoints = MODEL_ENDPOINTS
        logger.info("✅ Model Router ready (Local-First Strategy)")
    
    def route(self, task_classification: Dict) -> Dict:
        """Route vers le meilleur modèle"""
        
        task_type = task_classification.get("task_type", "unknown")
        
        logger.info(f"🔀 Routing task: {task_type}")
        
        rules = self.routing_rules.get(task_type, {})
        
        if not rules:
            logger.warning(f"No rules for {task_type}, using default")
            rules = self.routing_rules.get("code_implementation", {})
        
        primary_model = rules.get("primary", Model.MISTRAL)
        secondary_model = rules.get("secondary", Model.PHI)
        fallback_model = rules.get("fallback", Model.MISTRAL)
        
        endpoint = self.model_endpoints.get(primary_model, {})
        
        result = {
            "task_type": task_type,
            "selected_model": primary_model.value,
            "secondary_model": secondary_model.value,
            "fallback_model": fallback_model.value,
            "provider": "ollama_local",
            "endpoint": endpoint,
            "strategy": "local_first",
        }
        
        logger.info(f"✅ Route: {primary_model.value}")
        logger.info(f"   Secondary: {secondary_model.value}")
        logger.info(f"   Fallback: {fallback_model.value}")
        
        return result
    
    def batch_route(self, classifications: List[Dict]) -> List[Dict]:
        """Route plusieurs tâches"""
        
        logger.info(f"Batch routing {len(classifications)} tasks...")
        results = []
        for clf in classifications:
            result = self.route(clf)
            results.append(result)
        logger.info("Batch routing complete")
        return results

def demo():
    logger.info("\n" + "="*70)
    logger.info("🔀 MODEL ROUTER - DEMO")
    logger.info("="*70 + "\n")
    
    router = ModelRouter()
    
    test_classifications = [
        {"task_type": "code_implementation"},
        {"task_type": "explanation"},
        {"task_type": "data_analysis"},
        {"task_type": "system_design"},
    ]
    
    for clf in test_classifications:
        logger.info(f"\n[Task] {clf['task_type']}")
        result = router.route(clf)
        logger.info(f"   -> {result['selected_model']}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ DEMO COMPLETE\n")

if __name__ == "__main__":
    demo()
