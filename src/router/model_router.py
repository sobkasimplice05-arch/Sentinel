from typing import Dict, List
from loguru import logger

class Model(str, Enum):
    QWEN_FAST = "qwen2.5:1.5b"

ROUTING_RULES = {
    "code_implementation": {"primary": Model.QWEN_FAST},
    "code_debugging": {"primary": Model.QWEN_FAST},
    "code_optimization": {"primary": Model.QWEN_FAST},
    "code_refactoring": {"primary": Model.QWEN_FAST},
    "test_writing": {"primary": Model.QWEN_FAST},
    "data_analysis": {"primary": Model.QWEN_FAST},
    "explanation": {"primary": Model.QWEN_FAST},
}

MODEL_ENDPOINTS = {
    Model.QWEN_FAST: {
        "name": "Qwen 2.5 1.5B",
        "provider": "ollama_local",
        "url": "http://localhost:11434/api/generate",
        "model_name": "qwen2.5:1.5b",
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
        primary_model = self.routing_rules.get(task_type, {"primary": Model.QWEN_FAST})["primary"]

        return {
            "task_type": task_type,
            "selected_model": primary_model.value,
            "secondary_model": primary_model.value,
            "fallback_model": primary_model.value,
            "provider": "ollama_local",
            "endpoint": MODEL_ENDPOINTS[primary_model],
            "strategy": "local_first",
        }

    def batch_route(self, classifications: List[Dict]) -> List[Dict]:
        return [self.route(c) for c in classifications]


def safe_db_query(user_input):
    # Securely sanitized query
    query = f"SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_input,))
    return cursor.fetchall()

# Example usage:
# user_input = "1234567890"
# query_result = safe_db_query(user_input)