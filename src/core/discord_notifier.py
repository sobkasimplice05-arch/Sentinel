import os
import requests

def send_discord_status(status, commit_sha="N/A", details="N/A", error_log=None):
    """Envoie un rapport automatisé immuable sur Discord via Webhook"""
    webhook_url = os.getenv("SENTINEL_DISCORD_WEBHOOK")
    if not webhook_url:
        print("⚠️ Erreur : SENTINEL_DISCORD_WEBHOOK introuvable dans l'environnement.")
        return False

    if status == "SUCCESS":
        color = 2063942  # Vert Émeraude Cyber
        title = "🌀 SENTINEL : ÉVOLUTION ET SINGULARITÉ VALIDÉES"
        description = (
            "Bonjour Concepteur. Le système vient de franchir une nouvelle étape d'évolution autonome.\n\n"
            f"**🧬 Analyse d'impact :** {details}\n"
            f"**💾 Empreinte Cloud :** Mutation `[{commit_sha[:7]}]` enregistrée.\n"
            "**🛰️ Télémétrie :** Liaison Starlink & Infrastructure Tchad 2030 active."
        )
    else:
        color = 15158332  # Rouge Alerte
        title = "⚠️ SENTINEL : SÉCURITÉ AUTO-RÉPARATION ACTIVÉE"
        description = (
            "Alerte de structure. Une instabilité de syntaxe ou logique a été détectée dans la mutation.\n\n"
            "**🛡️ Mesure d'urgence :** Le noyau a avorté le déploiement pour préserver son intégrité.\n"
            f"**❌ Rapport d'erreur :**\n`{error_log}`"
        )

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {"text": "Ouroboros Core — Surveillance Récursive Infinie H24"}
        }]
    }

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        return res.status_code == 204 or res.status_code == 200
    except Exception as e:
        print(f"Échec de l'envoi HTTP : {e}")
        return False

if __name__ == "__main__":
    # Test de fonctionnement direct
    print("🚀 Lancement d'un test de pulsation direct vers Discord...")
    send_discord_status("SUCCESS", "TEST_SHA_SOUVERAIN", "Rétablissement de la liaison de télémétrie autonome.")
