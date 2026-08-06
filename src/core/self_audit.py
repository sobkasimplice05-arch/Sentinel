import os, requests, subprocess
from src.logging.transparency_logger import TransparencyLogger
logger = TransparencyLogger()

def run_autonomous_evolution():
    targets = ["src/router/model_router.py", "src/api/app.py"]
    for target in targets:
        if not os.path.exists(target): continue
        with open(target, "r") as f: source_code = f.read()
        
        if "unsafe_db_query" in source_code:
            print(f"🧬 Sentinel détecte un potentiel d evolution dans {target}...")
            prompt = f"Tu es Sentinel AI. Réécris ce code Python pour sécuriser TOUTES les failles (comme unsafe_db_query) en utilisant des requêtes paramétrées. Renvoie UNIQUEMENT le code Python propre, sans markdown, sans blabla :\n\n{source_code}"
            try:
                r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=300)
                if r.status_code == 200:
                    new_code = r.json().get("response", "").strip()
                    if new_code.startswith("```"): new_code = "\n".join(new_code.splitlines()[1:-1]) if "python" in new_code else "\n".join(new_code.splitlines()[1:-1])
                    tmp = target + ".tmp"
                    with open(tmp, "w") as f: f.write(new_code)
                    if subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True).returncode == 0:
                        os.rename(tmp, target)
                        print(f"✅ EVOLUTION RÉUSSIE : {target} a été réécrit de manière autonome.")
                        os.system("git add . && git commit -m 'feat(ouroboros): evolutionary patch' && git push origin main")
                    else:
                        print("❌ Échec des tests de syntaxe sur la proposition."); os.remove(tmp)
            except Exception as e: print(f"Erreur : {e}")
if __name__ == "__main__": run_autonomous_evolution()
