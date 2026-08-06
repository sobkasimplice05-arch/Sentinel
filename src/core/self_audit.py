import os, requests, subprocess
from src.logging.transparency_logger import TransparencyLogger
logger = TransparencyLogger()

def run_autonomous_evolution():
    target = "src/router/model_router.py"
    if not os.path.exists(target): return
    
    with open(target, "r") as f: source_code = f.read()
    
    # On cible uniquement la fonction vulnérable pour éviter de casser tout le fichier
    if "unsafe_db_query" in source_code:
        print(f"🧬 Sentinel active le mode d évolution stable pour {target}...")
        
        prompt = f"Tu es Sentinel AI. Voici une fonction Python vulnérable. Réécris-la uniquement pour sécuriser la faille avec une requête paramétrée SQL. Renvoie UNIQUEMENT le code Python de la fonction corrigée, sans markdown, sans blabla, sans toucher au reste :\\n\\ndef unsafe_db_query(user_input):"
        
        try:
            r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=300)
            if r.status_code == 200:
                patch = r.json().get("response", "").strip()
                if patch.startswith("```"): patch = "\\n".join(patch.splitlines()[1:-1])
                
                # RECONSTRUCTION HYBRIDE : On nettoie l injection et on injecte le patch propre
                clean_source = source_code.split("def unsafe_db_query")[0]
                stable_code = clean_source + "\\n" + patch + "\\n"
                
                tmp = target + ".tmp"
                with open(tmp, "w") as f: f.write(stable_code)
                
                # DOUBLE VÉRIFICATION LOCALE (Syntaxe + Pytest)
                syntax_check = subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True).returncode == 0
                
                if syntax_check:
                    os.rename(tmp, target)
                    # Lancement facultatif de pytest si disponible
                    pytest_check = subprocess.run(["pytest"], capture_output=True).returncode == 0
                    
                    if pytest_check:
                        print(f"✅ STABILISATION RÉUSSIE : {target} a évolué sans casser les tests.")
                        os.system("git add . && git commit -m 'feat(ouroboros): stable evolutionary patch applied' && git push origin main")
                        return
                    else:
                        print("❌ Évolution annulée : Le patch brise la suite de tests unitaires (Pytest). Rollback.")
                        os.system(f"git checkout -- {target}")
                else:
                    print("❌ Évolution annulée : Erreur de syntaxe détectée dans le patch.")
                    if os.path.exists(tmp): os.remove(tmp)
        except Exception as e: print(f"Erreur : {e}")

if __name__ == "__main__": run_autonomous_evolution()
