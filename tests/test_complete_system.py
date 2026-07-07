"""🧪 COMPLETE SYSTEM TESTS"""
import pytest
from src.sentinel_main import Sentinel
from loguru import logger
import time

@pytest.fixture
def sentinel():
    return Sentinel()

class TestCompleteSystem:
    def test_end_to_end(self, sentinel):
        """Complete end-to-end test"""
        result = sentinel.execute("Explain what is AI")
        assert result['success']
        assert result['quality_score'] >= 0.5
        logger.info("✅ test_end_to_end passed")
    
    def test_code_generation(self, sentinel):
        """Test code generation"""
        result = sentinel.execute("Write hello world in Python")
        if result['success']:
            assert "def " in result['response'] or "print" in result['response']
        logger.info("✅ test_code_generation passed")
    
    def test_performance(self, sentinel):
        """Test performance"""
        start = time.time()
        result = sentinel.execute("Say hello")
        elapsed = time.time() - start
        
        assert elapsed < 60  # Should complete in < 60s
        logger.info(f"✅ test_performance passed ({elapsed:.2f}s)")
    
    def test_quality_gate(self, sentinel):
        """Test quality gate"""
        result = sentinel.execute("Write code")
        assert 'quality_score' in result
        assert 0 <= result['quality_score'] <= 1
        logger.info("✅ test_quality_gate passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
