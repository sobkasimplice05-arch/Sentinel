"""
🔧 SELF-HEALING ENGINE - Sentinel auto-fixes her own errors
"""
import os
import json
import subprocess
import time
from datetime import datetime
from loguru import logger

class SelfHealing:
    def __init__(self):
        self.error_history = []
        self.solutions_applied = []
    
    def fix_ssh_conflict(self, error_msg):
        logger.info("🔑 Fixing SSH key conflict...")
        try:
            subprocess.run(["rm", "-f", "/home/runner/.ollama/id_ed25519"], timeout=5)
            subprocess.run(["pkill", "ollama"], timeout=5)
            logger.info("✅ SSH conflict resolved")
            return True
        except Exception as e:
            logger.error(f"❌ SSH fix failed: {e}")
            return False
    
    def fix_api_timeout(self, error_msg):
        logger.info("⏱️ Fixing API timeout...")
        try:
            config = {"groq": 180, "huggingface": 180, "replicate": 180}
            with open("api_timeout_config.json", "w") as f:
                json.dump(config, f)
            logger.info("✅ Timeout increased")
            return True
        except Exception as e:
            logger.error(f"❌ Timeout fix failed: {e}")
            return False
    
    def fix_api_auth_failed(self, error_msg):
        logger.info("🔐 Fixing API auth...")
        try:
            required_keys = ["GROQ_API_KEY", "HF_API_KEY", "REPLICATE_API_KEY", "GOOGLE_API_KEY"]
            missing = [k for k in required_keys if not os.environ.get(k)]
            if missing:
                logger.warning(f"⚠️ Missing: {missing}")
            logger.info("✅ API auth checked")
            return True
        except Exception as e:
            logger.error(f"❌ Auth fix failed: {e}")
            return False
    
    def fix_ollama(self, error_msg):
        logger.info("🦙 Fixing Ollama...")
        try:
            subprocess.run(["pkill", "ollama"], timeout=5)
            time.sleep(2)
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("✅ Ollama restarted")
            return True
        except Exception as e:
            logger.error(f"❌ Ollama fix failed: {e}")
            return False
    
    def log_solution(self, error_type, success):
        solution = {
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        self.solutions_applied.append(solution)
        try:
            with open("self_healing_log.json", "a") as f:
                f.write(json.dumps(solution) + "\n")
        except:
            pass

