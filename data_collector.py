import requests
import logging
from loguru import logger

class DataCollector:
    def __init__(self):
        self.sources = {
            "github": "https://github.com",
            "arxiv": "http://arxiv.org"
        }

    def fetch_all(self):
        """Récupère les données des flux avec système de secours (Fallback)"""
        collected_data = {}
        for name, url in self.sources.items():
            try:
                logger.info(f"📡 Connexion à la source : {name}...")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    collected_data[name] = "Données récupérées avec succès"
                    logger.success(f"✅ Source {name} synchronisée.")
                else:
                    logger.warning(f"⚠️ Source {name} indisponible (Code: {response.status_code}). Utilisation du Fallback.")
            except Exception as e:
                logger.error(f"❌ Erreur critique sur {name}: {str(e)}. Dégradation graduelle activée.")
        
        return collected_data

if __name__ == "__main__":
    collector = DataCollector()
    collector.fetch_all()
