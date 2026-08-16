import pytest
from src.core.self_audit import run_autonomous_evolution

def test_core_is_callable():
    assert callable(run_autonomous_evolution)
