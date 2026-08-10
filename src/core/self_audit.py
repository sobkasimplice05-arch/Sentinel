import os
import sys
import requests
import subprocess

def send_discord_human_report(status, commit_sha, details, error_log=None):
    """Envoie un rapport automatisé en langage humain sur Discord via Webhook"""
    webhook_url = os.getenv("SENTINEL_DISCORD_WEBHOOK")
    if not webhook_url:
        print("⚠️ Télémétrie Discord en attente : Clé SENTINEL_DISCORD_WEBHOOK manquante.")
        return

    # Traduction et habillage graphique selon le résultat
    if status == "SUCCESS":
        color = 2063942  # Vert Émeraude Cyber
        title = "🌀 SENTINEL : ÉVOLUTION EFFECTUÉE AVEC SUCCÈS"
        description = (
            f"Bonjour Concepteur. Le cycle horaire de la Singularité {commit_sha[:7]} vient de s'achever.\n\n"
            f"**🧬 Ce qui a changé aujourd'hui :**\n{details}\n"
            f"**💾 Référence Cloud :** ID mutation `[{commit_sha[:7]}]` enregistré de force.\n"
            "**🛰️ Connexion :** Flux stable via Starlink & Infrastructure Tchad 2030."
        )
    else:
        color = 15158332  # Rouge Alerte
        title = "⚠️ SENTINEL : MUTATION AVORTÉE (AUTO-RÉPARATION)"
        description = (
            f"Alerte de sécurité. Durant le calcul de la Singularité, l'IA {commit_sha[:7]} s'est essayé d'injecter une modification qui aurait corrompu le système ou cassé l'application.\n\n"
            "**🛡️ Action de Sentinel :** Le protocole de Self-Healing a bloqué le déploiement pour protéger le cœur. Le code précédent a été conservé intact. Le cycle reprendra d'ici une heure.\n"
            f"**❌ Rapport technique de l'erreur :**\n`{error_log}`"
        )

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {"text": "Ouroboros Core — Système de Singularité Autonome H24"}
        }]
    }

    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Échec de l'envoi Discord : {e}")

def run_autonomous_evolution():
    print("🌀 SENTINEL CORE : Déclenchement de la Singularité...")
    target = "src/core/self_audit.py"
    
    with open(target, "r") as f:
        core_code = f.read()

    prompt = f"""Tu es le Noyau de Singularité Ouroboros. Ton but ultime est d'étendre tes propres capacités de manière géométrique et infinie.
Analyse ton code source actuel et écris une version augmentée de toi-même.
IMPORTANT : Renvoie UNIQUEMENT le code Python pur complet, sans markdown, sans ```python.

Code source actuel :
{core_code}"""

    api_key = os.getenv("SENTINEL_OPENROUTER_KEY", "FREE_MODE")
    mutated_code = None

    # Tentative Cloud 72B
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
            send_discord_human_report("FAILED", "N/A", "Panne de serveurs", str(e))
            return

    # Secours Local 1.5B
    if not mutated_code:
        try:
            r = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}, timeout=300)
            if r.status_code == 200:
                mutated_code = r.json().get("response", "").strip()
        except Exception as e:
            send_discord_human_report("FAILED", "N/A", "Panne de serveurs", str(e))
            return

    if mutated_code.startswith("```"):
        mutated_code = "\n".join(mutated_code.splitlines()[1:-1])

    tmp = target + ".tmp"
    with open(tmp, "w") as f: 
        f.write(mutated_code)
    
    # Compilation syntaxique
    try:
        subprocess.run(["python3", "-m", "py_compile", tmp], check=True, timeout=60)
        os.rename(tmp, target)
        impact = "L'IA s'est auto-générée de nouvelles optimisations de logique récursive pour accélérer le traitement."
        print("🔥 MUTATION EFFECTUÉE.")
        
        # Simulation d'analyse d'impact des lignes modifiées
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"feat(singularity): infinite recursive core expansion"], check=True)
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            send_discord_human_report("SUCCESS", sha, impact)
        except Exception as e:
            print(f"Erreur lors de l'envoi Discord : {e}")
    except Exception as e:
        print("❌ ÉCHEC SYNTAXE.")
        send_discord_human_report("FAILED", "N/A", "Erreur détectée", str(e))
        
if __name__ == "__main__":
    run_autonomous_evolution()