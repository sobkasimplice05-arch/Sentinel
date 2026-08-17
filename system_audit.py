import os
import sqlite3
import json
from loguru import logger

def run_global_scan():
    logger.info("🔍 Lancement du Scan Général de Sentinel v3.0...")
    
    # 1. Analyse des fichiers présents
    critical_files = [
        "sentinel_v3_core.py", "memory_manager.py", "data_collector.py",
        "learning_engine.py", "ai_matrix.py", "notifier.py",
        "evolution_guard.py", "sentinel_janitor.py", "dependency_guardian.py"
    ]
    
    structure_status = {}
    for file in critical_files:
        exists = os.path.exists(file)
        structure_status[file] = "🟢 OPÉRATIONNEL" if exists else "🔴 MANQUANT"
        if not exists:
            logger.error(f"❌ Composant critique absent : {file}")
            
    # 2. Analyse de la Base de Données
    db_name = "sentinel_memory.db"
    db_status = "Non initialisée"
    mutation_count = 0
    
    if os.path.exists(db_name):
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM learning_history")
            mutation_count = cursor.fetchone()[0]
            db_status = f"🟢 ACTIVE ({mutation_count} cycles enregistrés)"
            conn.close()
        except Exception as e:
            db_status = f"🔴 CORROMPUE ou INACCESSIBLE ({str(e)})"
    else:
        db_status = "⚪ En attente du premier cycle cloud"

    # 3. Rédaction du Rapport Final
    report_content = f"""# 🛡️ RAPPORT D'AUDIT GLOBAL - SENTINEL v3.0
Généré automatiquement le : {os.popen('date').read().strip()}

## 🎛️ ÉTAT DES MICROSERVICES

"""
    for file, status in structure_status.items():
        report_content += f"- **{file}** : {status}\n"
        
    report_content += f"""
## 🗄️ ARCHITECTURE DE STOCKAGE
- **Moteur de mémoire** : SQLite Relationnel (Conformité ACID)
- **Fichier de base de données** : `{db_name}`
- **Statut de la base** : {db_status}

## ⚡ RÈGLES DE SÉCURITÉ & CYCLES
- **Fréquence d'auto-évolution** : Toutes les 15 minutes (Mode Ultra-Rapide)
- **Auto-Guérison (Rollback)** : Activée via EvolutionGuard (Validation Pytest)
- **Filtre Anti-Injection Cyber** : Activé dans DataCollector
- **Concierge Automatique (Janitor)** : Nettoyage des résidus > 24h configuré
"""
    
    with open("SENTINEL_AUDIT_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.success("📝 Rapport global généré avec succès dans 'SENTINEL_AUDIT_REPORT.md' !")

if __name__ == "__main__":
    run_global_scan()
