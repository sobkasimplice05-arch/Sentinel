import os
import sys

# Secret d'architecte : Ajoute automatiquement la racine au chemin Python
# Cela supprime définitivement l'obligation de taper $env:PYTHONPATH="."
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
