#!/bin/bash

echo "🔄 Vérification et initialisation de l'infrastructure Ollama..."

# Vérifier si Ollama est déjà lancé, sinon le démarrer proprement
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "🚀 Démarrage du serveur Ollama en arrière-plan..."
    ollama serve > /workspaces/Sentinel/ollama_server.log 2>&1 &
    
    # Attendre que le serveur soit totalement disponible
    until curl -s http://localhost:11434/api/tags > /dev/null; do
        sleep 2
    done
    echo "✅ Serveur Ollama actif."
else
    echo "✅ Le serveur Ollama est déjà en cours d'exécution."
fi

# S'assurer que le modèle de secours 1.5b est pré-téléchargé et disponible sur le disque
echo "📥 Vérification de la présence du modèle de secours qwen2.5:1.5b..."
ollama pull qwen2.5:1.5b

echo "🔥 DÉMARRAGE DE LA SINGULARITÉ DE 72 HEURES..."
# Lancer le processus persistant en tâche de fond (nohup)
nohup bash run_singularity_72h.sh > singularity_72h.log 2>&1 &

echo "🎯 Tout est synchronisé ! Tu peux éteindre ton PC portable."
