"""🧪 TESTS - Accuracy Coach"""
import pytest
from src.accuracy.accuracy_coach import AccuracyCoach
from loguru import logger

@pytest.fixture
def coach():
    return AccuracyCoach()

class TestAccuracyCoach:
    def test_initialization(self):
        coach = AccuracyCoach()
        assert coach is not None
        logger.info("✅ test_initialization passed")
    
    def test_evaluate_execution(self, coach):
        execution = {
            "instruction": "Write code",
            "model_used": "claude_code",
            "task_type": "code_implementation",
            "response": "def hello(): return 'world'",
            "quality_score": 0.9,
        }
        result = coach.evaluate_execution(execution)
        assert "effectiveness" in result
        assert "was_optimal" in result
        logger.info("✅ test_evaluate_execution passed")
    
    def test_model_stats(self, coach):
        execution = {
            "instruction": "Test",
            "model_used": "mistral",
            "task_type": "explanation",
            "response": "Good response",
            "quality_score": 0.85,
        }
        coach.evaluate_execution(execution)
        
        stats = coach.get_model_stats("mistral")
        assert stats["model"] == "mistral"
        assert stats["executions"] == 1
        logger.info("✅ test_model_stats passed")
    
    def test_recommendations(self, coach):
        execution = {
            "instruction": "Code",
            "model_used": "claude_code",
            "task_type": "code_implementation",
            "response": "def test(): pass",
            "quality_score": 0.9,
        }
        coach.evaluate_execution(execution)
        
        recommendations = coach.get_recommendations()
        assert "best_model" in recommendations
        assert "total_executions" in recommendations
        logger.info("✅ test_recommendations passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
