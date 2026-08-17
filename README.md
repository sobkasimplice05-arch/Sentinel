# 🛡️ Sentinel v3.0 — L'Orchestrateur d'IA Autonome Multi-LLM

**Sentinel v3.0** est une infrastructure de gouvernance et d'orchestration d'IA totalement décentralisée, résiliente et auto-évolutive. Inspiré du protocole de sécurité d'Elliot, ce système est conçu pour s'auto-évaluer, se nettoyer et se protéger contre les pannes ou les injections de code en temps réel toutes les 15 minutes.

Contrairement aux systèmes rigides, Sentinel v3.0 utilise une architecture en microservices autonomes pilotée par une matrice d'IA.

---

## ⚡ Architecture Visuelle des Microservices v3.0

Chaque composant de Sentinel fonctionne désormais comme un organe indépendant connecté au système nerveux central :

```text
       [ Flux Cyber Réeel : GitHub & ArXiv ]
                        │
                        ▼ (Cycle 15 min)
   1. 📡 DATA COLLECTOR (Désinfection anti-injection)
                        │
                        ▼
   2. 🧠 LEARNING ENGINE (Détection des patterns)
                        │
                        ▼
   3. 🤖 AI MATRIX (Matrice décisionnelle Qwen 2.5 1.5B)
                        │
                        ▼
   4. 🛡️ EVOLUTION GUARD (Validation Pytest & Auto-Guérison Rollback)
                        │
                        ▼
   5. 🗄️ MEMORY MANAGER (Base de données relationnelle SQL ACID)
                        │
                        ▼
       [ 📢 NOTIFIER : Alertes locales et distantes ]
                        │
                        ▼
       [ 🧼 JANITOR : Nettoyage automatique H24 ]
```

---

## ✨ Super-Pouvoirs de la Version 3.0

- **🧬 Auto-Évolution Autonome Rapide :** Le cœur distribué s'exécute toutes les 15 minutes via GitHub Actions pour analyser le web cyber et faire muter ses connaissances.
- **🛡️ Auto-Guérison Intégrée (Rollback) :** Si une modification de code casse les tests unitaires, `EvolutionGuard` intercepte l'erreur et déclenche une annulation instantanée (`git reset --hard`) pour revenir à l'état stable précédent.
- **🗄️ Mémoire Blindée (SQL Relationnel) :** Abandon des fichiers JSON fragiles au profit d'un moteur SQLite transactionnel conforme aux normes de sécurité ACID.
- **🧴 Protection Cyber Renforcée :** Désinfection automatique par expressions régulières de toutes les données du réseau pour bloquer les tentatives d'injection de scripts.
- **🧼 Concierge Automatique (Janitor) :** Nettoyage quotidien automatique des fichiers de sauvegarde obsolètes (`.bak`) pour préserver l'espace de stockage.

---

## 🛠️ Composition Technique du Dépôt

Le système s'articule autour de modules hautement spécialisés :
- `sentinel_v3_core.py` : Le chef d'orchestre central de l'infrastructure.
- `memory_manager.py` : Le gestionnaire de la base de données SQL relationnelle.
- `data_collector.py` : Le capteur cyber doté d'un filtre de nettoyage.
- `learning_engine.py` : Le moteur d'analyse des patterns cyber.
- `ai_matrix.py` : Le cerveau de routage multi-LLM (Qwen / Heuristique locale).
- `evolution_guard.py` : Le bouclier d'intégrité logicielle et de rollback.
- `notifier.py` : Le central d'alertes de mutations.
- `sentinel_janitor.py` : Le robot d'entretien et de purge.
- `dependency_guardian.py` : L'installateur dynamique de dépendances d'urgence.

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.12+
- Dépendances logicielles : `requests`, `loguru`, `pytest`

### Lancement du cycle manuellement
Pour simuler un cycle complet d'évolution en local et tester l'alignement des microservices, exécutez :
```bash
python sentinel_v3_core.py
```

*"Une IA conçue pour résister, s'adapter et évoluer sans jamais s'effondrer."* 🛡️
