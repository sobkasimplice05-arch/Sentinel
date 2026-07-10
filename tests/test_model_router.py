import pytest
from src.router.model_router import ModelRouter, Model

class TestModelRouter:
    @pytest.fixture
    def router(self):
        return ModelRouter()
    
    def test_initialization(self, router):
        assert router is not None
    
    # ✅ TOUS les routes utilisent maintenant QWEN_LIGHT (lightweight)
    def test_route_code(self, router):
        result = router.route({"task_type": "code_implementation"})
        assert result["selected_model"] == "qwen2.5:0.5b"
        assert result["provider"] == "ollama_local"
    
    def test_route_data(self, router):
        result = router.route({"task_type": "data_analysis"})
        assert result["selected_model"] == "qwen2.5:0.5b"
        assert result["provider"] == "ollama_local"
    
    def test_route_explanation(self, router):
        result = router.route({"task_type": "explanation"})
        assert result["selected_model"] == "qwen2.5:0.5b"
        assert result["provider"] == "ollama_local"
    
    def test_batch_route(self, router):
        classifications = [
            {"task_type": "code_implementation"},
            {"task_type": "explanation"},
            {"task_type": "data_analysis"}
        ]
        results = router.batch_route(classifications)
        assert len(results) == 3
        assert all(r["selected_model"] == "qwen2.5:0.5b" for r in results)
