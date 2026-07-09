"""🔀 MODEL ROUTER - Version Légère"""
from typing import Dict, List
from loguru import logger
from enum import Enum

class Model(str, Enum):
    QWEN_LIGHT = "qwen2.5:0.5b"

ROUTING_RULES = {
    "code_implementation": {"primary": Model.QWEN_LIGHT},
    "code_debugging": {"primary": Model.QWEN_LIGHT},
    "data_analysis": {"primary": Model.QWEN_LIGHT},
    "explanation": {"primary": Model.QWEN_LIGHT},
}

MODEL_ENDPOINTS = {
    Model.QWEN_LIGHT: {
        "name": "Qwen 2.5 0.5B",
        "provider": "ollama_local",
        "url": "http://localhost:11434",
        "model_name": "qwen2.5:0.5b",
        "max_tokens": 500,
    },
}

class ModelRouter:
    def __init__(self):
        logger.info("🔀 Model Router (Lightweight)...")
        self.routing_rules = ROUTING_RULES
        self.model_endpoints = MODEL_ENDPOINTS
        logger.info("✅ Ready")
    
    def route(self, task_classification: Dict) -> Dict:
        return {
            "task_type": task_classification.get("task_type"),
            "selected_model": "qwen2.5:0.5b",
            "secondary_model": "qwen2.5:0.5b",
            "fallback_model": "qwen2.5:0.5b",
            "provider": "ollama_local",
            "endpoint": MODEL_ENDPOINTS[Model.QWEN_LIGHT],
            "strategy": "local_first",
        }
    
    def batch_route(self, classifications: List[Dict]) -> List[Dict]:
        return [self.route(c) for c in classifications]
