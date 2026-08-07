"""🧪 TESTS - LLM Orchestrator"""
import pytest
from src.orchestrator.llm_orchestrator import LLMOrchestrator
from src.router.model_router import ModelRouter
from loguru import logger

@pytest.fixture
def orchestrator():
    return LLMOrchestrator()

@pytest.fixture
def router():
    return ModelRouter()

class TestLLMOrchestrator:
    def test_initialization(self):
        orch = LLMOrchestrator()
        assert orch is not None
        logger.info("✅ test_initialization passed")
    
    def test_execute_structure(self, orchestrator, router):
        routing = router.route({"task_type": "explanation"})
        result = orchestrator.execute(routing, "Say hello")
        assert "success" in result
        assert "model_used" in result
        logger.info("✅ test_execute_structure passed")
    
    def test_batch_execute(self, orchestrator, router):
        routings = [
            router.route({"task_type": "explanation"}),
            router.route({"task_type": "code_implementation"})
        ]
        instructions = ["Say hello", "Write code"]
        
        results = orchestrator.batch_execute(routings, instructions)
        assert len(results) == 2
        logger.info("✅ test_batch_execute passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
