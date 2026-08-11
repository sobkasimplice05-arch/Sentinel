"""
🌐 EXTERNAL MODELS CONFIGURATION - Free APIs
"""

MODELS_CONFIG = {
    "local": {
        "qwen": {
            "endpoint": "http://localhost:11434/api/generate",
            "model": "qwen2.5:1.5b",
            "speed": "fast",
            "cost": "free"
        }
    },
    "external": {
        "groq_llama": {
            "endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.1-70b-versatile",
            "api_key_env": "GROQ_API_KEY",
            "speed": "ultra-fast",
            "cost": "free"
        },
        "together_mistral": {
            "endpoint": "https://api.together.xyz/v1/chat/completions",
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "api_key_env": "TOGETHER_API_KEY",
            "speed": "fast",
            "cost": "free"
        },
        "huggingface": {
            "endpoint": "https://api-inference.huggingface.co/models",
            "model": "meta-llama/Llama-2-70b-chat-hf",
            "api_key_env": "HF_API_KEY",
            "speed": "medium",
            "cost": "free"
        },
        "google_gemini": {
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
            "model": "gemini-1.5-pro",
            "api_key_env": "GOOGLE_API_KEY",
            "speed": "fast",
            "cost": "free"
        }
    }
}

def get_best_model_for_task(task_type):
    """Sélectionne le meilleur modèle pour la tâche"""
    if task_type == "fast_mutation":
        return MODELS_CONFIG["external"]["groq_llama"]
    elif task_type == "quality_mutation":
        return MODELS_CONFIG["external"]["together_mistral"]
    elif task_type == "aggressive_mutation":
        return MODELS_CONFIG["external"]["huggingface"]
    else:
        return MODELS_CONFIG["local"]["qwen"]

