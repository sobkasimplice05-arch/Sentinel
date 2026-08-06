import os, requests, subprocess

def run_autonomous_evolution():
    target = "src/blockchain/arbitrum_saas_factory.py"
    
    # Structure initiale si le fichier n'existe pas encore
    if not os.path.exists(target):
        initial_code = 'class ArbitrumSaaSFactory:\n    """\n    Usine autonome de Smart Contracts SaaS pour Arbitrum.\n    Sentinel conçoit, audite et déploie des fonctionnalités monétisables.\n    """\n    def __init__(self):\n        self.network = "Arbitrum One"\n'
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as f: f.write(initial_code)

    with open(target, "r") as f: source_code = f.read()
    
    print(f"🧬 Sentinel initie son cycle d evolution Web3 sur {target}...")
    
    prompt = f"""Tu es l'architecte Web3 de Sentinel AI. Ton but est de faire évoluer ce fichier pour coder des Smart Contracts Solidity sous forme de services SaaS automatisés et monétisables sur Arbitrum (ex: ponts de jetons, coffres-forts DeFi sécurisés, usines à jetons ERC-20/NFT).
Génère de nouvelles fonctions de code Python robustes, sécurisées et prêtes pour la production.

Code actuel :
{source_code}

Renvoie UNIQUEMENT le code Python complet mis à jour et enrichi, sans aucun blabla, sans markdown."""

    try:
        # Requête vers Ollama local (ou l'API de secours dans le Cloud)
        r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=300)
        if r.status_code == 200:
            new_code = r.json().get("response", "").strip()
            if new_code.startswith("```"): new_code = "\n".join(new_code.splitlines()[1:-1])
            
            tmp = target + ".tmp"
            with open(tmp, "w") as f: f.write(new_code)
            
            if subprocess.run(["python3", "-m", "py_compile", tmp], capture_output=True).returncode == 0:
                os.rename(tmp, target)
                print(f"✅ ÉVOLUTION WEB3 RÉUSSIE : {target} a été enrichi d'un nouveau module SaaS.")
            else:
                if os.path.exists(tmp): os.remove(tmp)
    except Exception as e:
        print(f"Mode Cloud passif : En attente du prochain cycle d'écriture. (Détails: {e})")

if __name__ == "__main__":
    run_autonomous_evolution()
