"""
🧪 TESTS - Instruction Parser
Tests unitaires pour le parser d'instructions
"""

import pytest
from src.core.instruction_parser import (
    InstructionParser, Intent, Language, Domain, Complexity
)
from loguru import logger


@pytest.fixture
def parser():
    """Fixture pour le parser"""
    return InstructionParser()


class TestInstructionParserBasic:
    """Tests basiques"""
    
    def test_initialization(self):
        """Test l'initialisation"""
        parser = InstructionParser()
        assert parser is not None
        logger.info("✅ test_initialization passed")
    
    def test_empty_input(self, parser):
        """Test avec input vide"""
        result = parser.parse("")
        assert result["success"] is False
        logger.info("✅ test_empty_input passed")
    
    def test_returns_dict(self, parser):
        """Test que parse retourne un dict"""
        result = parser.parse("write code")
        assert isinstance(result, dict)
        assert "intent" in result
        assert "language" in result
        assert "domain" in result
        logger.info("✅ test_returns_dict passed")


class TestIntentDetection:
    """Tests de détection d'intent"""
    
    def test_write_code_intent(self, parser):
        """Détecte l'intent WRITE_CODE"""
        result = parser.parse("Write a Python function")
        assert result["intent"] == Intent.WRITE_CODE.value
        logger.info("✅ test_write_code_intent passed")
    
    def test_debug_intent(self, parser):
        """Détecte l'intent DEBUG"""
        result = parser.parse("Debug this broken code")
        assert result["intent"] == Intent.DEBUG_CODE.value
        logger.info("✅ test_debug_intent passed")
    
    def test_explain_intent(self, parser):
        """Détecte l'intent EXPLAIN"""
        result = parser.parse("Explain how algorithms work")
        assert result["intent"] == Intent.EXPLAIN.value
        logger.info("✅ test_explain_intent passed")


class TestLanguageDetection:
    """Tests de détection de langage"""
    
    def test_python_detection(self, parser):
        """Détecte Python"""
        result = parser.parse("Write a Python function")
        assert result["language"] == Language.PYTHON.value
        logger.info("✅ test_python_detection passed")
    
    def test_javascript_detection(self, parser):
        """Détecte JavaScript"""
        result = parser.parse("Create a React component")
        assert result["language"] == Language.JAVASCRIPT.value
        logger.info("✅ test_javascript_detection passed")
    
    def test_sql_detection(self, parser):
        """Détecte SQL"""
        result = parser.parse("Write a SQL query")
        assert result["language"] == Language.SQL.value
        logger.info("✅ test_sql_detection passed")


class TestDomainDetection:
    """Tests de détection de domaine"""
    
    def test_web_domain(self, parser):
        """Détecte domaine WEB"""
        result = parser.parse("Build a React website")
        assert result["domain"] == Domain.WEB.value
        logger.info("✅ test_web_domain passed")
    
    def test_data_science_domain(self, parser):
        """Détecte domaine DATA_SCIENCE"""
        result = parser.parse("Analyze data with pandas")
        assert result["domain"] == Domain.DATA_SCIENCE.value
        logger.info("✅ test_data_science_domain passed")
    
    def test_algorithms_domain(self, parser):
        """Détecte domaine ALGORITHMS"""
        result = parser.parse("Implement sorting algorithm")
        assert result["domain"] == Domain.ALGORITHMS.value
        logger.info("✅ test_algorithms_domain passed")


class TestComplexityEstimation:
    """Tests d'estimation de complexité"""
    
    def test_simple_complexity(self, parser):
        """Estime complexité SIMPLE"""
        result = parser.parse("hello")
        assert result["complexity"] == Complexity.SIMPLE.value
        logger.info("✅ test_simple_complexity passed")
    
    def test_complex_complexity(self, parser):
        """Estime complexité COMPLEX"""
        result = parser.parse("Implement a complex recursive algorithm optimization")
        assert result["complexity"] in [Complexity.COMPLEX.value, Complexity.MEDIUM.value]
        logger.info("✅ test_complex_complexity passed")


class TestConfidenceScoring:
    """Tests du scoring de confiance"""
    
    def test_confidence_range(self, parser):
        """Confiance entre 0 et 1"""
        result = parser.parse("Write Python code")
        assert 0 <= result["confidence"] <= 1
        logger.info("✅ test_confidence_range passed")
    
    def test_clear_intent_high_confidence(self, parser):
        """Intent clair = confiance élevée"""
        result = parser.parse("Write a Python function for calculating fibonacci")
        assert result["confidence"] > 0.7
        logger.info("✅ test_clear_intent_high_confidence passed")


class TestBatchProcessing:
    """Tests du batch processing"""
    
    def test_batch_parse(self, parser):
        """Parse multiple instructions"""
        instructions = [
            "Write Python code",
            "Debug JavaScript",
            "Explain ML"
        ]
        results = parser.batch_parse(instructions)
        assert len(results) == len(instructions)
        assert all(isinstance(r, dict) for r in results)
        logger.info("✅ test_batch_parse passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
