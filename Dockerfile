FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Variables d'environnement par défaut
ENV PORT=8000
ENV HOST=0.0.0.0
ENV DEV_MODE=false
ENV TEST_MODE=false

EXPOSE 8000

# Lancement du serveur FastAPI en production
CMD ["python3", "src/api/app.py"]
