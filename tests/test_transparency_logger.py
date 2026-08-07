"""🧪 TESTS - Transparency Logger"""
import pytest
from src.logging.transparency_logger import TransparencyLogger
from loguru import logger
import tempfile

@pytest.fixture
def logger_with_temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield TransparencyLogger(log_dir=tmpdir)

class TestTransparencyLogger:
    def test_initialization(self):
        tl = TransparencyLogger()
        assert tl is not None
        logger.info("✅ test_initialization passed")
    
    def test_log_execution(self, logger_with_temp_dir):
        tl = logger_with_temp_dir
        
        execution = {
            "original_instruction": "Write code",
            "cleaned_instruction": "Write code",
            "task_type": "code_implementation",
            "selected_model": "claude_code",
            "response": "def hello(): pass",
            "quality_score": 0.9,
        }
        
        exec_id = tl.log_execution(execution)
        assert exec_id is not None
        assert "exec_" in exec_id
        logger.info("✅ test_log_execution passed")
    
    def test_get_execution_log(self, logger_with_temp_dir):
        tl = logger_with_temp_dir
        
        execution = {
            "original_instruction": "Test",
            "task_type": "explanation",
            "response": "Good",
            "quality_score": 0.85,
        }
        
        exec_id = tl.log_execution(execution)
        log = tl.get_execution_log(exec_id)
        
        assert log["execution_id"] == exec_id
        logger.info("✅ test_get_execution_log passed")
    
    def test_generate_summary(self, logger_with_temp_dir):
        tl = logger_with_temp_dir
        
        for i in range(3):
            tl.log_execution({
                "task_type": "code",
                "response": f"Response {i}",
                "quality_score": 0.9,
            })
        
        summary = tl.generate_summary()
        assert summary["total_executions"] == 3
        logger.info("✅ test_generate_summary passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
