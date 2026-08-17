import sys
import subprocess
from loguru import logger

def enforce_dependencies():
    """Vérifie et installe dynamiquement les packages manquants pour éviter les Run Failed cloud"""
    required_packages = ["requests", "loguru", "pytest"]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            logger.warning(f"🛡️ Guardian : Package '{package}' manquant. Installation d'urgence...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
                logger.success(f"✅ Package '{package}' injecté avec succès.")
            except Exception as e:
                logger.critical(f"❌ Impossible d'installer '{package}': {str(e)}")

if __name__ == "__main__":
    enforce_dependencies()
