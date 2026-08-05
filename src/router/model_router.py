"""🔀 MODEL ROUTER - Version Légère"""
from typing import Dict, List
from loguru import logger
from enum import Enum

class Model(str, Enum):
    QWEN_LIGHT = "qwen2.5:0.5b"
    QWEN_MEDIUM = "qwen2.5:1.0b"

ROUTING_RULES = {
    "code_implementation": {"primary": Model.QWEN_LIGHT},
    "code_debugging": {"primary": Model.QWEN_LIGHT},
    "code_optimization": {"primary": Model.QWEN_LIGHT},
    "code_refactoring": {"primary": Model.QWEN_LIGHT},
    "test_writing": {"primary": Model.QWEN_LIGHT},
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
    Model.QWEN_MEDIUM: {
        "name": "Qwen 2.5 1.0B",
        "provider": "ollama_local",
        "url": "http://localhost:11434",
        "model_name": "qwen2.5:1.0b",
        "max_tokens": 1000,
    },
}

class ModelRouter:
    def __init__(self):
        logger.info("🔀 Model Router (Lightweight)...")
        self.routing_rules = ROUTING_RULES
        self.model_endpoints = MODEL_ENDPOINTS
        logger.info("✅ Ready")
    
    def route(self, task_classification: Dict) -> Dict:
        task_type = task_classification.get("task_type", "explanation")
        primary_model = self.routing_rules.get(task_type, {"primary": Model.QWEN_LIGHT})["primary"]
        secondary_model = Model.QWEN_MEDIUM if primary_model == Model.QWEN_LIGHT else Model.QWEN_LIGHT

        return {
            "task_type": task_type,
            "selected_model": primary_model.value,
            "secondary_model": secondary_model.value,
            "fallback_model": Model.QWEN_MEDIUM.value,
            "provider": "ollama_local",
            "endpoint": MODEL_ENDPOINTS[primary_model],
            "strategy": "local_first",
        }
    
    def batch_route(self, classifications: List[Dict]) -> List[Dict]:
        return [self.route(c) for c in classifications]
