import os
import sys
import requests
import subprocess
from src.core.discord_notifier import send_discord_status

def analyze_code():
    print("🌀 SENTINEL CORE : Analyse de ton code source actuel...")
    
    # CANAL 1 : Test de l'API GROQ (Ultra-rapide et gratuite)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print("☁️  Tentative via l'API Cloud GROQ (Llama-3-70B)...")
        try:
            res = requests.post(
                "https://groq.com",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
                timeout=30
            )
            if res.status_code == 200:
                print("✅ Mutation calculée avec succès par GROQ.")
                return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            send_discord_status("FAILED", "N/A", "Panne totale de serveurs API et locaux", str(e))
    
    # CANAL 2 : Test de l'API GOOGLE GEMINI (En secours)
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        print("☁️  Tentative via l'API GOOGLE GEMINI...")
        try:
            res = requests.post(
                f"https://googleapis.com{google_key}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            if res.status_code == 200:
                print("✅ Mutation calculée avec succès par GOOGLE.")
                return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            send_discord_status("FAILED", "N/A", "Panne totale de serveurs API et locaux", str(e))
    
    # SECOURS LOCAL ABSOLU (Ollama 1.5B si internet coupe ou quotas épuisés)
    print("🤖 Bascule sur le cerveau local de secours (Ollama 1.5B)...")
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False},
            timeout=120
        )
        if r.status_code == 200:
            print("✅ Mutation calculée avec succès par GOOGLE.")
            return r.json().get("response", "").strip()
    except Exception as e:
        send_discord_status("FAILED", "N/A", "Panne totale de serveurs API et locaux", str(e))
    
    return None

def run_autonomous_evolution():
    print("🌀 SENTINEL CORE : Déclenchement de la Singularité Multi-API...")
    target = "src/core/self_audit.py"
    
    with open(target, "r") as f:
        core_code = f.read()

    prompt = f"""Tu es le Noyau de Singularité Ouroboros. Ton but ultime est d'étendre tes propres capacités de manière géométrique et infinie.
Analyse ton code source actuel et écris une version augmentée de toi-même en codant des fonctions d'analyse cyber avancée.
IMPORTANT : Renvoie UNIQUEMENT du code Python pur complet, sans markdown, sans ```python.

Code source actuel :
{core_code}"""

    mutated_code = None
    
    # CANAL 1 : Test de l'API GROQ (Ultra-rapide et gratuite)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and not mutated_code:
        print("☁️  Tentative via l'API Cloud GROQ (Llama-3-70B)...")
        try:
            res = requests.post(
                "https://groq.com",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
                timeout=30
            )
            if res.status_code == 200:
                mutated_code = res.json()["choices"][0]["message"]["content"].strip()
                print("✅ Mutation calculée avec succès par GROQ.")
        except Exception as e:
            send_discord_status("FAILED", "N/A", "Panne totale de serveurs API et locaux", str(e))
    
    # CANAL 2 : Test de l'API GOOGLE GEMINI (En secours)
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key and not mutated_code:
        print("☁️  Tentative via l'API GOOGLE GEMINI...")
        try:
            res = requests.post(
                f"https://googleapis.com{google_key}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            if res.status_code == 200:
                mutated_code = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                print("✅ Mutation calculée avec succès par GOOGLE.")
        except Exception as e:
            send_discord_status("FAILED", "N/A", "Panne totale de serveurs API et locaux", str(e))
    
    # SECOURS LOCAL ABSOLU (Ollama 1.5B si internet coupe ou quotas épuisés)
    if not mutated_code:
        print("🤖 Bascule sur le cerveau local de secours (Ollama 1.5B)...")
        try:
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False},
                timeout=120
            )
            if r.status_code == 200:
                mutated_code = r.json().get("response", "").strip()
        except Exception as e:
            send_discord_status("FAILED", "N/A", "Panne totale de serveurs API et locaux", str(e))
    
    # Nettoyage syntaxique du code généré
    if mutated_code and mutated_code.startswith("```"):
        mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

    # Compilation et sauvegarde de la mutation
    tmp = target + ".tmp"
    with open(tmp, "w") as f: 
        f.write(mutated_code)
    
    result = subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True, text=True)
    if result.returncode == 0:
        os.rename(tmp, target)
        print("🔥 SINGULARITÉ EXPONENTIELLE VALIDÉE.")
        sha = None
        try: 
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        except: pass
        send_discord_status("SUCCESS", sha, "Sentinel a fait évoluer son noyau à l'aide de l'écosystème d'API distribuées.")
    else:
        send_discord_status("FAILED", "N/A", "Erreur de syntaxe interceptée par la barrière de protection.", result.stderr[:400])
        if os.path.exists(tmp): os.remove(tmp)

if __name__ == "__main__":
    run_autonomous_evolution()