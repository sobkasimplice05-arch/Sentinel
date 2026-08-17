import requests
import re
from loguru import logger

class DataCollector:
    def __init__(self):
        self.sources = {
            "github": "https://github.com",
            "arxiv": "http://arxiv.org"
        }

    def sanitize_input(self, text):
        """Filtre les caractères dangereux pour bloquer les injections de code (Sécurité Elliot v3)"""
        if not isinstance(text, str):
            return str(text)
        # Supprime les scripts malveillants et caractères de requêtes malveillantes
        clean_text = re.sub(r'[<>;\'"|]', '', text)
        return clean_text

    def fetch_all(self):
        collected_data = {}
        for name, url in self.sources.items():
            try:
                logger.info(f"📡 Connexion sécurisée à : {name}...")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Désinfection des données reçues du Web
                    safe_content = self.sanitize_input(response.text[:500])
                    collected_data[name] = safe_content
                    logger.success(f"✅ Source {name} vérifiée et désinfectée.")
                else:
                    logger.warning(f"⚠️ Source {name} indisponible (Code: {response.status_code}).")
            except Exception as e:
                logger.error(f"❌ Dégradation graduelle sur {name}: {str(e)}")
        
        return collected_data

if __name__ == "__main__":
    collector = DataCollector()
    collector.fetch_all()
