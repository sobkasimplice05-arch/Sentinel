import os
import sys
import requests
import subprocess
from src.core.discord_notifier import send_discord_status

def run_autonomous_evolution():
    print("🌀 SENTINEL CORE : Déclenchement de la Singularité...")
    target = "src/core/self_audit.py"
    
    with open(target, "r") as f:
        core_code = f.read()

    prompt = f"Tu es le Noyau de Singularité Ouroboros. Analyse ton code source actuel et écris une version augmentée de toi-même en codant des fonctions d'analyse cyber avancée. Renvoie UNIQUEMENT le code Python pur complet, sans markdown.\n\nCode source actuel :\n{core_code}"

    api_key = os.getenv("SENTINEL_OPENROUTER_KEY", "FREE_MODE")
    mutated_code = None

    if api_key != "FREE_MODE":
        try:
            res = requests.post(
                url="https://openrouter.ai",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "qwen/qwen-2.5-72b-instruct:free", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3},
                timeout=45
            )
            if res.status_code == 200:
                mutated_code = res.json()["choices"]["message"]["content"].strip()
        except: pass

    if not mutated_code:
        try:
            r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=120)
            if r.status_code == 200:
                mutated_code = r.json().get("response", "").strip()
        except Exception as e:
            send_discord_status("FAILED", "N/A", "Panne de serveurs", str(e))
            return

    if mutated_code and mutated_code.startswith("```"):
        mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

    tmp = target + ".tmp"
    with open(tmp, "w") as f: f.write(mutated_code)
    
    result = subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True, text=True)
    if result.returncode == 0:
        os.rename(tmp, target)
        os.system("git add . && git commit -m 'feat(ouroboros): autonomous cloud evolution - H24 Ouroboros mutation' && git push origin main --force")
        try:
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        except:
            sha = "UNKNOWN_SHA"
        send_discord_status("SUCCESS", sha, "Sentinel a fait évoluer son noyau récursif avec succès dans la matrice.")
    else:
        send_discord_status("FAILED", "N/A", "Erreur de syntaxe interceptée", result.stderr[:400])
        if os.path.exists(tmp): os.remove(tmp)

if __name__ == "__main__":
    run_autonomous_evolution()
