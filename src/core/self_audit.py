import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime

MEMORY_PATH = "src/core/circular_memory.json"

def load_circular_memory():
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "last_cycle_status": "INIT",
        "successful_mutations": 0,
        "consecutive_failures": 0,
        "preferred_model": "None",
        "sentinel_mood_notes": "Première étincelle de conscience circulaire."
    }

def save_circular_memory(memory):
    try:
        with open(MEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=4)
    except:
        pass

def ensure_ollama_is_running():
    try:
        r = requests.get("http://localhost:11434/", timeout=5)
        if r.status_code == 200:
            return True
    except:
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
            r = requests.get("http://localhost:11434/", timeout=5)
            if r.status_code == 200:
                return True
        except:
            pass
    return False

def fetch_cyber_intel_free():
    try:
        res = requests.get("https://circl.lu", timeout=10)
        if res.status_code == 200 and isinstance(res.json(), list):
            vulnerabilities = [item.get("summary", "") for item in res.json()[:3]]
            return "\n".join([f"- [CVE INTEL] {v}" for v in vulnerabilities])
    except:
        pass
    return "- Ingestion standard des directives de protection Ouroboros."

def run_autonomous_evolution():
    print("🌀 NOYAU SOUVERAIN OUROBOROS : Activation de la Réplication...")
    target = "src/core/self_audit.py"
    cycle_num = int(os.environ.get("GITHUB_RUN_NUMBER", 1))
    memory = load_circular_memory()
    
    with open(target, "r") as f:
        core_code = f.read()

    web_intel = fetch_cyber_intel_free()
    prompt = f"Tu es l'Ouroboros. Analyse ton code source et réécris-toi récursivement.\nIntel:\n{web_intel}\nCode:\n{core_code}"

    api_sequence = [
        ("GROQ", "https://groq.com", os.getenv("GROQ_API_KEY"), {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}),
        ("GOOGLE", f"https://googleapis.com{os.getenv('GOOGLE_API_KEY')}", os.getenv("GOOGLE_API_KEY"), {"contents": [{"parts": [{"text": prompt}]}]})
    ]

    mutated_code = None
    model_used = "Inconnu"
    
    for provider, url, key, payload in api_sequence:
        if key and not mutated_code:
            try:
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"} if provider == "GROQ" else {"Content-Type": "application/json"}
                res = requests.post(url, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    mutated_code = res.json()["choices"]["message"]["content"].strip() if provider == "GROQ" else res.json()["candidates"]["content"]["parts"]["text"].strip()
                    model_used = provider
            except:
                pass

    if not mutated_code and ensure_ollama_is_running():
        try:
            r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=45)
            if r.status_code == 200:
                mutated_code = r.json().get("response", "").strip()
                model_used = "qwen2.5:1.5b"
        except:
            pass

    if not mutated_code:
        print("⚠️ Aucun modèle réactif. Mise en veille sécurisée.")
        memory["last_cycle_status"] = "STANDBY"
        save_circular_memory(memory)
        sys.exit(0)

    if mutated_code.startswith("```"):
        mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

    tmp = target + ".tmp"
    with open(tmp, "w") as f:
        f.write(mutated_code)
    
    if subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True).returncode == 0:
        os.rename(tmp, target)
        memory["last_cycle_status"] = "SUCCESS"
        memory["successful_mutations"] += 1
        memory["preferred_model"] = model_used
        save_circular_memory(memory)
        print("🔥 MUTATION EFFECTUÉE AVEC SUCCÈS.")
    else:
        if os.path.exists(tmp):
            os.remove(tmp)
        memory["last_cycle_status"] = "SYNTAX_REJECTED"
        save_circular_memory(memory)
        print("❌ Échec de la validation syntaxique. Code préservé.")
    sys.exit(0)

if __name__ == "__main__":
    run_autonomous_evolution()
