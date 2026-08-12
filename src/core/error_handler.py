"""
🔴 ERROR HANDLER - Track all failures
"""
import json
from datetime import datetime
from loguru import logger

class ErrorTracker:
    def __init__(self):
        self.errors = []
        self.error_log = "error_tracking.json"
    
    def log_error(self, cycle_num, error_type, error_msg, timestamp=None):
        """Log une erreur avec détails"""
        error_entry = {
            "cycle": cycle_num,
            "type": error_type,  # "api_error", "syntax_error", "timeout", etc
            "message": error_msg,
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        self.errors.append(error_entry)
        
        # Sauve dans fichier
        with open(self.error_log, "a") as f:
            f.write(json.dumps(error_entry) + "\n")
        
        logger.error(f"❌ [{error_type}] Cycle {cycle_num}: {error_msg}")
    
    def get_last_errors(self, count=5):
        """Get les 5 dernières erreurs"""
        try:
            with open(self.error_log, "r") as f:
                lines = f.readlines()
                return [json.loads(line) for line in lines[-count:]]
        except:
            return []

