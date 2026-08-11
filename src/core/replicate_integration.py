"""
🌀 SENTINEL REPLICATE INTEGRATION
Permet l'utilisation de REPLICATE_API_KEY pour l'inférence de modèles avancés.
"""

import os
import requests

def run_replicate_model(prompt, model_version="latest", extra_params=None):
    api_key = os.getenv("REPLICATE_API_KEY")
    if not api_key:
        print("⚠️ Avertissement : REPLICATE_API_KEY non définie dans l'environnement.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Endpoint par défaut pour l'inférence Replicate
    url = "https://api.replicate.com/v1/predictions"
    
    payload = {
        "input": {
            "prompt": prompt,
            **(extra_params or {})
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Erreur Replicate API : {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception lors de l'appel Replicate : {e}")
        return None
