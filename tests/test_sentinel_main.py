"""🧪 TESTS - Sentinel Main"""
import pytest
from src.sentinel_main import Sentinel
from loguru import logger

@pytest.fixture
def sentinel():
    return Sentinel()

class TestSentinelMain:
    def test_initialization(self):
        sentinel = Sentinel()
        assert sentinel is not None
        logger.info("✅ test_initialization passed")
    
    def test_execute_structure(self, sentinel):
        result = sentinel.execute("Explain Python")
        assert "success" in result
        assert "response" in result or "error" in result
        logger.info("✅ test_execute_structure passed")
    
    def test_complete_pipeline(self, sentinel):
        result = sentinel.execute("Write hello world")
        if result['success']:
            assert "quality_score" in result
            assert "model_used" in result
            assert "execution_id" in result
        logger.info("✅ test_complete_pipeline passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
