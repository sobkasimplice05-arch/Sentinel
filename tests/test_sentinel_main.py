import pytest
from src.core.self_audit import run_autonomous_evolution

def test_core_initialization():
    assert run_autonomous_evolution is not None
