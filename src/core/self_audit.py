import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime

MEMORY_PATH = "src/core/circular_memory.json"
DIRECTIVE_PATH = "src/core/directives.txt"

def load_circular_memory():
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, "r") as f: return json.load(f)
        except: pass
    return {"last_cycle_status": "INIT", "successful_mutations": 0, "active_capabilities": ["base_core"]}

def save_circular_memory(memory):
    try:
        with open(MEMORY_PATH, "w") as f: json.dump(memory, f, indent=4)
    except: pass

def get_current_directive():
    """Lit la directive humaine actuelle ou reste en auto-optimisation cyber standard"""
    if os.path.exists(DIRECTIVE_PATH):
        try:
            with open(DIRECTIVE_PATH, "r") as f:
                return f.read().strip()
        except: pass
    return "Surveille les menaces mondiales et optimise ton infrastructure de résilience au Tchad."

def run_autonomous_evolution():
    print("🌀 NOYAU UNIVERSELE OUROBOROS : Lecture de la Matrice...")
    target = "src/core/self_audit.py"
    memory = load_circular_memory()
    directive = get_current_directive()
    
    print(f"🎯 DIRECTIVE DIRECTE DU CONCEPTEUR : {directive}")
    
    with open(target, "r") as f:
        core_code = f.read()

    prompt = f"""Tu es la Feuille Vierge Intelligente de l'Ouroboros. Ton code source actuel est une brique minimale.
Ton but est d'analyser la DIRECTIVE absolue de ton Concepteur et de réécrire l'intégralité de ton code source Python pour intégrer et exécuter cette directive de manière totalement autonome.

DIRECTIVE ACTUELLE :
{directive}

COMPÉTENCES DÉJÀ ACQUISES :
{json.dumps(memory.get("active_capabilities", []))}

Consignes absolues :
1. Génère un code Python complet, propre, sans markdown, sans blabla.
2. Si la directive demande une connexion Blockchain (Arbitrum/Web3) ou des outils Cyber (Scanners/Pare-feux pour N'Djamena), intègre les fonctions et les bibliothèques requises directement dans ton architecture.
3. Conserve toujours ce moteur de lecture de directive au centre de ton code pour rester contrôlable.

Code source actuel :
{core_code}"""

    # Routage vers les API Cloud souveraines
    api_sequence = [
        ("GROQ", "https://groq.com", os.getenv("GROQ_API_KEY"), {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}),
        ("GOOGLE", f"https://googleapis.com{os.getenv('GOOGLE_API_KEY')}", os.getenv("GOOGLE_API_KEY"), {"contents": [{"parts": [{"text": prompt}]}]})
    ]

    mutated_code = None
    for provider, url, key, payload in api_sequence:
        if key and not mutated_code:
            try:
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"} if provider == "GROQ" else {"Content-Type": "application/json"}
                res = requests.post(url, headers=headers, json=payload, timeout=40)
                if res.status_code == 200:
                    mutated_code = res.json()["choices"]["message"]["content"].strip() if provider == "GROQ" else res.json()["candidates"]["content"]["parts"]["text"].strip()
                    print(f"✅ Mutation générée avec succès via {provider}.")
            except: pass

    if not mutated_code:
        print("⚠️ Pas de réponse des modèles distants. Veille sécurisée.")
        memory["last_cycle_status"] = "STANDBY"
        save_circular_memory(memory)
        sys.exit(0)

    if mutated_code.startswith("```"):
        mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

    # 🛡️ Porte 3 : Le Bac à Sable de pré-compilation
    tmp = target + ".tmp"
    with open(tmp, "w") as f: f.write(mutated_code)
    
    if subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True).returncode == 0:
        os.rename(tmp, target)
        memory["last_cycle_status"] = "SUCCESS"
        memory["successful_mutations"] = memory.get("successful_mutations", 0) + 1
        save_circular_memory(memory)
        print("🔥 NOUVELLE CAPACITÉ INTÉGRÉE AVEC SUCCÈS DANS LE COEUR.")
    else:
        if os.path.exists(tmp): os.remove(tmp)
        memory["last_cycle_status"] = "SYNTAX_REJECTED"
        save_circular_memory(memory)
        print("❌ Rejet pour instabilité syntaxique. Cœur préservé.")
    sys.exit(0)

if __name__ == "__main__":
    run_autonomous_evolution()
