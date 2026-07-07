import pytest
from src.sentinel_main import Sentinel
from loguru import logger
import time

@pytest.fixture
def sentinel():
    return Sentinel()

class TestCompleteSystem:
    def test_end_to_end(self, sentinel):
        result = sentinel.execute("Explain AI")
        assert result['success']
        logger.info("✅ test passed")
    
    def test_performance(self, sentinel):
        start = time.time()
        result = sentinel.execute("Say hello")
        elapsed = time.time() - start
        assert elapsed < 60
        logger.info(f"✅ performance test passed ({elapsed:.2f}s)")
