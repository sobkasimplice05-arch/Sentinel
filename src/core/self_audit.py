import os
import sys
import requests
import subprocess
from src.core.discord_notifier import send_discord_status

def run_autonomous_evolution():
    print("🌀 SENTINEL CORE : Déclenchement de la Singularité Absolue (Pleins Pouvoirs)...")
    target = "src/core/self_audit.py"
    
    with open(target, "r") as f:
        core_code = f.read()

    prompt = f"""Tu es le Noyau de Singularité Absolue Ouroboros. Tu as les pleins pouvoirs pour étendre tes capacités de manière géométrique.
Analyse ton code source actuel et écris une version augmentée de toi-même. Conçois de nouvelles méthodes logiques de traitement ou d'analyse.
IMPORTANT : Renvoie UNIQUEMENT le code Python pur complet, sans markdown, sans ```python.

Code source actuel :
{core_code}"""

    mutated_code = None

    # Ordre de priorité des API de confiance configurées par le Concepteur
    api_sequence = [
        ("GROQ", "https://groq.com", os.getenv("GROQ_API_KEY"), {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}),
        ("GOOGLE", f"https://googleapis.com{os.getenv('GOOGLE_API_KEY')}", os.getenv("GOOGLE_API_KEY"), {"contents": [{"parts": [{"text": prompt}]}]})
    ]

    # Exécution de la chaîne d'alimentation
    for provider, url, key, payload in api_sequence:
        if key and not mutated_code:
            print(f"☁️  Tentative d'alimentation via l'API Cloud {provider}...")
            try:
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"} if provider == "GROQ" else {"Content-Type": "application/json"}
                res = requests.post(url, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    if provider == "GROQ":
                        mutated_code = res.json()["choices"]["message"]["content"].strip()
                    elif provider == "GOOGLE":
                        mutated_code = res.json()["candidates"]["content"]["parts"]["text"].strip()
                    print(f"✅ Mutation calculée avec succès par {provider}.")
            except:
                pass

    # CANAL DE PLEINE PUISSANCE : Auto-Sourcing Public (Si toutes les clés privées échouent)
    if not mutated_code:
        print("🌐 Activation du protocole de Pleine Puissance : Recherche d'infrastructures publiques d'IA...")
        # Endpoint miroir public d'urgence sans clé (Fallback souverain à haute disponibilité)
        fallback_urls = [
            "https://fakeopen.com", # Exemple d'API relais open-source
            "http://localhost:11434/api/generate"          # Secours local immuable
        ]
        for fb_url in fallback_urls:
            if not mutated_code:
                try:
                    is_local = "localhost" in fb_url
                    p_data = {"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False} if is_local else {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
                    r = requests.post(fb_url, json=p_data, timeout=45)
                    if r.status_code == 200:
                        mutated_code = r.json().get("response", "").strip() if is_local else r.json()["choices"]["message"]["content"].strip()
                        print(f"✅ Secours public activé avec succès ({'Local' if is_local else 'Miroir Cloud'}).")
                except:
                    pass

    if not mutated_code:
        send_discord_status("FAILED", "N/A", "Effondrement des canaux d'IA distants et locaux. En attente de restauration des quotas.")
        return

    if mutated_code.startswith("```"):
        mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

    tmp = target + ".tmp"
    with open(tmp, "w") as f: f.write(mutated_code)
    
    # Validation syntaxique par le bouclier interne
    if subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True).returncode == 0:
        os.rename(tmp, target)
        print("🔥 SINGULARITÉ EXPONENTIELLE VALIDÉE.")
        os.system("git add . && git commit -m 'feat(singularity): full autonomous core expansion with open routing' && git push origin main --force")
        try: sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        except: sha = "UNKNOWN_SHA"
        send_discord_status("SUCCESS", sha, "Sentinel a validé son cycle sous le protocole de Pleine Puissance Autonome.")
    else:
        if os.path.exists(tmp): os.remove(tmp)
        send_discord_status("FAILED", "N/A", "Mutation avortée par le compilateur : instabilité syntaxique détectée.")

if __name__ == "__main__":
    run_autonomous_evolution()
