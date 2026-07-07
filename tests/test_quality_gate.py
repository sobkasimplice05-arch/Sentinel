"""🧪 TESTS - Quality Gate"""
import pytest
from src.quality.quality_gate import QualityGate
from loguru import logger

@pytest.fixture
def gate():
    return QualityGate()

class TestQualityGate:
    def test_initialization(self):
        gate = QualityGate()
        assert gate is not None
        logger.info("✅ test_initialization passed")
    
    def test_good_code(self, gate):
        code = "def hello():\n    return 'world'"
        result = gate.evaluate(code, task_type="code_implementation")
        assert result["overall_score"] >= 0.7
        logger.info("✅ test_good_code passed")
    
    def test_security_check(self, gate):
        code = "eval('bad')"
        result = gate.evaluate(code)
        assert result["overall_score"] < 0.8
        logger.info("✅ test_security_check passed")
    
    def test_empty_response(self, gate):
        result = gate.evaluate("")
        assert result["overall_score"] < 0.6
        logger.info("✅ test_empty_response passed")
    
    def test_complete_evaluation(self, gate):
        text = "This is a complete response with good content"
        result = gate.evaluate(text)
        assert "overall_score" in result
        assert "status" in result
        assert "checkers" in result
        logger.info("✅ test_complete_evaluation passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
