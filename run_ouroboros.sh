#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [ -d "venv" ]; then
  echo "🔧 Activating virtual environment..."
  # shellcheck source=/dev/null
  source "venv/bin/activate"
else
  echo "⚠️ Virtual environment not found at $PROJECT_ROOT/venv"
  echo "Please create it first with: python -m venv venv"
  exit 1
fi

echo "📦 Running syntax check on source only..."
python -m compileall src

echo "🚀 Starting FastAPI app with Uvicorn..."
# Bind to 0.0.0.0 so the app is reachable from outside the container/VM
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
