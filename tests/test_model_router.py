"""🧪 TESTS - Model Router"""
import pytest
from src.router.model_router import ModelRouter, Model
from loguru import logger

@pytest.fixture
def router():
    return ModelRouter()

class TestModelRouter:
    def test_initialization(self):
        router = ModelRouter()
        assert router is not None
        logger.info("✅ test_initialization passed")
    
    def test_route_code(self, router):
        result = router.route({"task_type": "code_implementation"})
        assert result["selected_model"] == Model.CLAUDE_CODE.value
        logger.info("✅ test_route_code passed")
    
    def test_route_data(self, router):
        result = router.route({"task_type": "data_analysis"})
        assert result["selected_model"] == Model.DEEPSEEK.value
        logger.info("✅ test_route_data passed")
    
    def test_route_explanation(self, router):
        result = router.route({"task_type": "explanation"})
        assert result["selected_model"] == Model.MISTRAL.value
        logger.info("✅ test_route_explanation passed")
    
    def test_batch_route(self, router):
        tasks = [
            {"task_type": "code_implementation"},
            {"task_type": "explanation"}
        ]
        results = router.batch_route(tasks)
        assert len(results) == 2
        logger.info("✅ test_batch_route passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
