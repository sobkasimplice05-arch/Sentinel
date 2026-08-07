"""
Configuration pytest - Active le mode TEST automatiquement pour les tests
"""
import os
import pytest

# Activer le mode test pour tous les tests
os.environ["TEST_MODE"] = "true"

def pytest_configure(config):
    """Hook pytest pour la configuration initiale"""
    print("\n" + "="*70)
    print("🔧 PYTEST CONFIGURATION")
    print("="*70)
    print("📋 Mode: TEST (Réponses mock activées)")
    print("="*70 + "\n")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configure l'environnement de test avant tous les tests"""
    os.environ["TEST_MODE"] = "true"
    print("\n✅ Mode TEST activé pour tous les tests")
    yield
    print("\n✅ Tests terminés")
