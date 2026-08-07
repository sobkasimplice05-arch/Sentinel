#!/usr/bin/env bash
cd /home/ubuntu/Sentinel
export PYTHONPATH=.
export DEV_MODE=false
export TEST_MODE=false
export ENABLE_PERIODIC_AUDIT=true

echo "======================================================"
echo "🚀 DÉMARRAGE DU SITE WEB PERMANENT SENTINEL AI (PORT 8000)"
echo "======================================================"

while true; do
    python3 src/api/app.py
    echo "⚠️ Serveur arrêté. Redémarrage automatique dans 5 secondes..."
    sleep 5
done
