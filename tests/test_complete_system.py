import pytest
from src.sentinel_main import Sentinel
from loguru import logger
import time
import os

@pytest.fixture
def sentinel():
    """Crée une instance Sentinel en mode test"""
    # Activer le mode test
    os.environ["TEST_MODE"] = "true"
    return Sentinel()

@pytest.fixture
def sentinel_production():
    """Crée une instance Sentinel en mode production (pour tests manuels)"""
    os.environ["TEST_MODE"] = "false"
    return Sentinel()

class TestCompleteSystem:
    def test_end_to_end(self, sentinel):
        """Test du pipeline complet avec réponses mock"""
        result = sentinel.execute("Explain AI")
        assert result['success'], f"Expected success but got: {result}"
        assert result['response'], "Expected response content"
        assert 'AI' in result['response'] or 'Artificial' in result['response']
        logger.info("✅ test_end_to_end passed")
    
    def test_performance(self, sentinel):
        """Test de performance du système"""
        start = time.time()
        result = sentinel.execute("Say hello")
        elapsed = time.time() - start
        assert elapsed < 60, f"Performance test failed: {elapsed}s > 60s"
        assert result['success'], f"Expected success but got: {result}"
        logger.info(f"✅ performance test passed ({elapsed:.2f}s)")
    
    def test_multiple_instructions(self, sentinel):
        """Test avec plusieurs instructions différentes"""
        instructions = [
            "Explain AI",
            "Say hello",
            "Write hello world"
        ]
        
        for instruction in instructions:
            result = sentinel.execute(instruction)
            assert result['success'], f"Failed for instruction: {instruction}"
            assert result['response'], f"No response for: {instruction}"
        
        logger.info("✅ test_multiple_instructions passed")
    
    def test_response_structure(self, sentinel):
        """Valide la structure de la réponse"""
        result = sentinel.execute("Explain AI")
        
        # Vérifier les champs obligatoires
        assert 'success' in result
        assert 'response' in result
        assert 'model_used' in result
        
        # Vérifier les types
        assert isinstance(result['success'], bool)
        assert isinstance(result['response'], str)
        assert isinstance(result['model_used'], str)
        
        logger.info("✅ test_response_structure passed")
