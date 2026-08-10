import os
import sys
import requests
import subprocess

def run_autonomous_evolution():
    print("🌀 SENTINEL CORE : Déclenchement de la Singularité et de l'Auto-Correction...")
    
    target = "src/core/self_audit.py"

    with open(target, "r") as f:
        core_code = f.read()

    # Récupération de la clé API OpenRouter pour le modèle 72B
    api_key = os.getenv("SENTINEL_OPENROUTER_KEY", "FREE_MODE")

    for tentative in range(3): 
        print(f"🧬 Tentative de mutation {tentative + 1}/3...")
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
            except Exception as e:
                print(f"❌ Erreur lors de la tentative {tentative + 1}: {e}")

        if not mutated_code: 
            try:
                r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=300)
                if r.status_code == 200:
                    mutated_code = r.json().get("response", "").strip()
            except Exception as e:
                print(f"❌ Erreur lors de la tentative {tentative + 1}: {e}")

        if mutated_code.startswith("```"):
            mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

        # Validation de la syntaxe par compilation
        tmp = target + ".tmp"
        with open(tmp, "w") as f: 
            f.write(mutated_code)
        
        result = subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True, text=True)
        if result.returncode == 0:
            os.rename(tmp, target)
            print("🔥 SINGULARITÉ EXPONENTIELLE VALIDÉE : Mutation sans erreur installée.")
            os.system("git add . && git commit -m 'feat(singularity): successful recursive self-healing mutation' && git push origin main --force")
            return
        else:
            print(f"⚠️ Erreur de syntaxe détectée. Ajustement du prompt avec le rapport d'erreur pour la prochaine tentative...")
            # On enrichit le prompt avec l'erreur brute renvoyée par Python pour que l'IA comprenne sa faute
            prompt = f"Le code que tu as généré a échoué avec l'erreur suivante :\n{result.stderr}\nRéécris-le en corrigeant impérativement cette erreur de syntaxe.\n\nCode source d'origine :\n{core_code}"
            if os.path.exists(tmp): 
                os.remove(tmp)

    print("❌ Les 3 tentatives ont échoué. Conservation du noyau d'origine pour ce cycle.")

if __name__ == "__main__":
    run_autonomous_evolution()