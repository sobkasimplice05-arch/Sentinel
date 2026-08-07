"""
🧪 TESTS - Grammar Corrector Input
Tests unitaires pour le correcteur grammatical
"""

import pytest
from src.quality.grammar_corrector import GrammarCorrectorInput

@pytest.fixture(scope="module")
def corrector():
    return GrammarCorrectorInput(language="en")

class TestGrammarCorrectorBasic:
    def test_initialization(self):
        corrector = GrammarCorrectorInput(language="en")
        assert corrector is not None
        assert corrector.language == "en"
    
    def test_empty_input(self, corrector):
        result = corrector.correct("")
        assert result["original"] == ""
        assert result["corrected"] == ""
        assert result["confidence"] == 1.0
    
    def test_correct_text_returns_dict(self, corrector):
        result = corrector.correct("hello world")
        assert isinstance(result, dict)
        assert "original" in result
        assert "corrected" in result
        assert "changes" in result
        assert "confidence" in result
    
    def test_confidence_score(self, corrector):
        result = corrector.correct("the quick brown fox")
        assert 0 <= result["confidence"] <= 1

class TestGrammarCorrectorCorrections:
    def test_space_normalization(self, corrector):
        result = corrector.correct("hello    world")
        assert "    " not in result["corrected"]
    
    def test_grammar_error_detection(self, corrector):
        result = corrector.correct("he go to school")
        assert len(result["changes"]) > 0 or result["confidence"] < 1.0
    
    def test_batch_correct(self, corrector):
        texts = ["hello world", "i am student"]
        results = corrector.batch_correct(texts)
        assert len(results) == len(texts)

class TestGrammarCorrectorMetadata:
    def test_change_count(self, corrector):
        result = corrector.correct("he go")
        assert "change_count" in result
        assert isinstance(result["change_count"], int)
    
    def test_device_reported(self, corrector):
        result = corrector.correct("hello")
        assert "device" in result
    
    def test_should_process_flag(self, corrector):
        result = corrector.correct("hello")
        assert isinstance(result["should_process"], bool)
