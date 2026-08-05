"""📊 TRANSPARENCY LOGGER - Log tout en JSON
Chaque décision, chaque réponse, tout est auditable
"""

from logging.handlers import RotatingFileHandler
from typing import Dict, List, Any
from loguru import logger
from datetime import datetime
import json
from pathlib import Path
import re
import logging

LOG_REDACT_PATTERNS = [
    (re.compile(r"\bpassword\b\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE), "[REDACTED]"),
    (re.compile(r"\bapi[_-]?key\b\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE), "[REDACTED]"),
    (re.compile(r"\bsecret\b\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE), "[REDACTED]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED]"),
]

class TransparencyLogger:
    """Logue chaque exécution pour transparence totale"""
    
    def __init__(self, log_dir: str = "logs"):
        logger.info("📊 Initializing Transparency Logger...")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.execution_count = 0
        self._configure_rotation()
        logger.info("✅ Transparency Logger ready")
    
    def _configure_rotation(self) -> None:
        log_file = self.log_dir / "sentinel.log"
        handler = RotatingFileHandler(str(log_file), maxBytes=5_000_000, backupCount=3)
        handler.setLevel(logging.INFO)
        logger.add(handler)
    
    def _redact(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        for pattern, replacement in LOG_REDACT_PATTERNS:
            text = pattern.sub(lambda m: m.group(0).split('=')[0] + "= [REDACTED]", text)
        return text
    
    def _redact_dict(self, data: Dict) -> Dict:
        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = self._redact(value)
            elif isinstance(value, dict):
                redacted[key] = self._redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [self._redact_dict(item) if isinstance(item, dict) else self._redact(item) if isinstance(item, str) else item for item in value]
            else:
                redacted[key] = value
        return redacted
    
    def log_execution(self, execution_data: Dict) -> str:
        """Logue une exécution complète"""
        
        self.execution_count += 1
        execution_id = f"exec_{self.execution_count:05d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"📊 Logging execution {execution_id}...")
        
        execution_data = self._redact_dict(execution_data)
        
        log_entry = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            
            # Input
            "input": {
                "original": execution_data.get("original_instruction", ""),
                "cleaned": execution_data.get("cleaned_instruction", ""),
            },
            
            # Parsing
            "parsing": {
                "intent": execution_data.get("intent"),
                "language": execution_data.get("language"),
                "domain": execution_data.get("domain"),
                "complexity": execution_data.get("complexity"),
                "parse_confidence": execution_data.get("parse_confidence", 0),
            },
            
            # Classification
            "classification": {
                "task_type": execution_data.get("task_type"),
                "sub_category": execution_data.get("sub_category"),
                "priority": execution_data.get("priority_level"),
                "estimated_effort": execution_data.get("estimated_effort"),
                "classify_confidence": execution_data.get("classify_confidence", 0),
            },
            
            # Routing
            "routing": {
                "selected_model": execution_data.get("selected_model"),
                "secondary_model": execution_data.get("secondary_model"),
                "fallback_model": execution_data.get("fallback_model"),
                "strategy": execution_data.get("strategy", "local_first"),
            },
            
            # Execution
            "execution": {
                "model_used": execution_data.get("model_used"),
                "attempt": execution_data.get("attempt", 1),
                "fallback_used": execution_data.get("fallback_used", False),
                "execution_time_seconds": execution_data.get("execution_time", 0),
            },
            
            # Quality
            "quality": {
                "overall_score": execution_data.get("quality_score", 0),
                "syntax_score": execution_data.get("syntax_score", 0),
                "logic_score": execution_data.get("logic_score", 0),
                "security_score": execution_data.get("security_score", 0),
                "hallucination_score": execution_data.get("hallucination_score", 0),
                "completeness_score": execution_data.get("completeness_score", 0),
                "status": execution_data.get("quality_status", "UNKNOWN"),
            },
            
            # Accuracy
            "accuracy": {
                "effectiveness": execution_data.get("effectiveness", 0),
                "was_optimal": execution_data.get("was_optimal", False),
                "feedback": execution_data.get("feedback", ""),
                "suggestion": execution_data.get("suggestion", ""),
            },
            
            # Output
            "output": {
                "response": execution_data.get("response", "")[:500],  # First 500 chars
                "response_length": len(execution_data.get("response", "")),
            },
            
            # Metadata
            "metadata": {
                "user_id": execution_data.get("user_id", "anonymous"),
                "session_id": execution_data.get("session_id", ""),
                "version": "1.0",
            }
        }
        
        # Save to JSON file
        log_file = self.log_dir / f"{execution_id}.json"
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        logger.info(f"✅ Logged to {log_file}")
        
        return execution_id
    
    def get_execution_log(self, execution_id: str) -> Dict:
        """Récupère un log d'exécution"""
        
        log_file = self.log_dir / f"{execution_id}.json"
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                return json.load(f)
        
        return {"error": f"Execution {execution_id} not found"}
    
    def get_all_logs(self, limit: int = 10) -> List[Dict]:
        """Récupère les derniers logs"""
        
        log_files = sorted(self.log_dir.glob("*.json"), reverse=True)[:limit]
        logs = []
        
        for log_file in log_files:
            with open(log_file, 'r') as f:
                logs.append(json.load(f))
        
        return logs
    
    def generate_summary(self) -> Dict:
        """Génère un résumé des exécutions"""
        
        logger.info("📊 Generating execution summary...")
        
        logs = self.get_all_logs(limit=100)
        
        if not logs:
            return {"message": "No executions logged yet"}
        
        # Calculate statistics
        total_executions = len(logs)
        avg_quality = sum(log["quality"]["overall_score"] for log in logs) / total_executions
        
        task_types = {}
        for log in logs:
            task = log["classification"]["task_type"]
            task_types[task] = task_types.get(task, 0) + 1
        
        models_used = {}
        for log in logs:
            model = log["execution"]["model_used"]
            models_used[model] = models_used.get(model, 0) + 1
        
        return {
            "total_executions": total_executions,
            "average_quality_score": round(avg_quality, 2),
            "task_types_distribution": task_types,
            "models_used_distribution": models_used,
            "logs_directory": str(self.log_dir),
        }

def demo():
    logger.info("\n" + "="*70)
    logger.info("📊 TRANSPARENCY LOGGER - DEMO")
    logger.info("="*70 + "\n")
    
    tl = TransparencyLogger()
    
    test_execution = {
        "original_instruction": "Write a Python function",
        "cleaned_instruction": "Write a Python function",
        "intent": "write_code",
        "language": "python",
        "domain": "algorithms",
        "complexity": "medium",
        "task_type": "code_implementation",
        "priority_level": "medium",
        "selected_model": "claude_code",
        "model_used": "claude_code",
        "quality_score": 0.92,
        "response": "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "effectiveness": 0.95,
        "was_optimal": True,
    }
    
    execution_id = tl.log_execution(test_execution)
    logger.info(f"\n✅ Execution logged with ID: {execution_id}")
    
    summary = tl.generate_summary()
    logger.info(f"\n📊 Summary:")
    logger.info(f"   Total: {summary['total_executions']}")
    logger.info(f"   Avg quality: {summary['average_quality_score']:.0%}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ TRANSPARENCY LOGGER WORKING\n")

if __name__ == "__main__":
    demo()
