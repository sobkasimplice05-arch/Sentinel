"""
🧪 TEST-DRIVEN MUTATIONS
Les mutations qui FIXENT les tests cassés
"""
import subprocess
import os
from loguru import logger

class TestDrivenEvolution:
    def get_failing_tests(self):
        """Récupère les tests qui échouent"""
        logger.info("🧪 Running tests to find failures...")
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ All tests pass - generating aggressive mutations")
            return None
        
        # Parse les erreurs
        failures = result.stdout.split("FAILED")[1:] if "FAILED" in result.stdout else []
        logger.warning(f"⚠️ {len(failures)} tests failing")
        return failures
    
    def generate_fix_mutation(self, failures):
        """Génère une mutation qui FIXE les tests"""
        if not failures:
            return self.generate_aggressive_mutation()
        
        failure_summary = "\n".join(failures[:3])  # Top 3 failures
        
        prompt = f"""Les tests suivants échouent:

{failure_summary}

Génère une mutation qui FIXE CES ERREURS SPÉCIFIQUES.
Improve le code pour passer tous les tests.

Code actuel:
{open('src/core/self_audit.py').read()}

Nouveau code (Python pur):"""
        
        logger.info("🧬 Generating mutation to fix tests...")
        return prompt
    
    def generate_aggressive_mutation(self):
        """Si tous tests pass, mutations agressives"""
        prompt = """Tous les tests passent! Génère une mutation AGRESSIVE:
1. Ajoute 3 nouvelles fonctions
2. Optimise la performance x10
3. Ajoute du multi-threading
4. Ajoute de la mémorisation
5. Ajoute un système de cache

Sois créatif et ambitieux! (500+ lignes)"""
        return prompt

