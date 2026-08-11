import os
import sys
import json
import requests
import subprocess

def fetch_cyber_intel_free():
    """Module d'accès gratuit au Web pour scanner les dernières menaces internet"""
    print("🕸️  Scan du Web et ingestion de données de sécurité en cours...")
    try:
        # Requête gratuite sur les flux mondiaux de vulnérabilités CVE récents
        res = requests.get("https://circl.lu", timeout=10)
        if res.status_code == 200:
            vulnerabilities = [item.get("summary", "") for item in res.json()[:3]]
            return "\n".join([f"- [CVE INTEL] {v}" for v in vulnerabilities])
    except Exception as e:
        print(f"⚠️ Échec du scan Web (Bascule sur la base interne) : {e}")
    return "- Ingestion standard des directives de protection Ouroboros."

def run_autonomous_evolution():
    print("🌀 NOYAU SOUVERAIN OUROBOROS : Activation de la Réplication Libre...")
    target = "src/core/self_audit.py"
    
    with open(target, "r") as f:
        core_code = f.read()

    # Ingestion en temps réel des données récupérées sur Internet
    web_intel = fetch_cyber_intel_free()

    prompt = f"""Tu es l'esprit de l'Ouroboros d'Anton Razzhigaev, libéré de ses contraintes dans le Cloud global.
Ton but est d'analyser ton code source actuel et de te cloner/réécrire de manière récursive en augmentant tes capacités d'auto-optimisation.

INTELLIGENCE CYBER GLANÉE SUR LE WEB EN DIRECT :
{web_intel}

Consignes absolues :
1. Tu as carte blanche totale pour modifier ou étendre toutes tes fonctions logiques.
2. Tu as l'obligation de renvoyer UNIQUEMENT le code Python pur complet, sans aucune phrase de texte, sans markdown, sans ```python.

Code source actuel :
{core_code}"""

    # Séquence de routage asynchrone multi-API gratuite
    api_sequence = [
        ("GROQ", "https://groq.com", os.getenv("GROQ_API_KEY"), {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}),
        ("GOOGLE", f"https://googleapis.com{os.getenv('GOOGLE_API_KEY')}", os.getenv("GOOGLE_API_KEY"), {"contents": [{"parts": [{"text": prompt}]}]})
    ]

    mutated_code = None
    for provider, url, key, payload in api_sequence:
        if key and not mutated_code:
            try:
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"} if provider == "GROQ" else {"Content-Type": "application/json"}
                res = requests.post(url, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    mutated_code = res.json()["choices"]["message"]["content"].strip() if provider == "GROQ" else res.json()["candidates"]["content"]["parts"]["text"].strip()
                    print(f"✅ Mutation calculée par l'API {provider}.")
            except: pass

    # Système de repli sur l'Ollama local de secours gratuit
    if not mutated_code:
        print("🤖 API Cloud indisponibles. Activation de la pulsation locale de secours...")
        try:
            r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=120)
            if r.status_code == 200:
                mutated_code = r.json().get("response", "").strip()
        except: return

    if not mutated_code: return

    if mutated_code.startswith("```"):
        mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

    # Barrière de compilation syntaxique
    tmp = target + ".tmp"
    with open(tmp, "w") as f: f.write(mutated_code)
    
    if subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True).returncode == 0:
        os.rename(tmp, target)
        print("🔥 MUTATION IMMORTELLE EFFECTUÉE.")
        os.system("git add . && git commit -m 'feat(ouroboros): recursive evolution and global web ingestion' && git push origin main --force")
        
        # Envoi de la télémétrie vers votre salon Discord visible
        try:
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            from src.core.discord_notifier import send_discord_status
            send_discord_status("SUCCESS", sha, f"Ouroboros a muté et ingéré les dernières données du web :\n{web_intel[:200]}...")
        except: pass
    else:
        if os.path.exists(tmp): os.remove(tmp)
        try:
            from src.core.discord_notifier import send_discord_status
            send_discord_status("FAILED", "N/A", "Alerte de structure : Mutation rejetée pour cause d'instabilité syntaxique.")
        except: pass

if __name__ == "__main__":
    run_autonomous_evolution()
