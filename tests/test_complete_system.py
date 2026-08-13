import pytest
from src.core.self_audit import run_autonomous_evolution

def test_sentinel_core_exists():
    """Vérifie simplement que la brique d'évolution autonome est bien présente et exécutable"""
    assert callable(run_autonomous_evolution)
