"""🧪 TESTS - Task Classifier"""
import pytest
from src.classifier.task_classifier import TaskClassifier, TaskType
from src.core.instruction_parser import InstructionParser
from loguru import logger

@pytest.fixture
def classifier():
    return TaskClassifier()

@pytest.fixture
def parser():
    return InstructionParser()

class TestTaskClassifier:
    def test_initialization(self):
        classifier = TaskClassifier()
        assert classifier is not None
        logger.info("✅ test_initialization passed")
    
    def test_code_implementation(self, classifier, parser):
        parse_result = parser.parse("Write a Python function")
        classify_result = classifier.classify(parse_result)
        assert classify_result["task_type"] == TaskType.CODE_IMPLEMENTATION.value
        logger.info("✅ test_code_implementation passed")
    
    def test_debug_detection(self, classifier, parser):
        parse_result = parser.parse("Debug this code")
        classify_result = classifier.classify(parse_result)
        assert classify_result["task_type"] == TaskType.CODE_DEBUGGING.value
        logger.info("✅ test_debug_detection passed")
    
    def test_confidence(self, classifier, parser):
        parse_result = parser.parse("Write code")
        classify_result = classifier.classify(parse_result)
        assert 0 <= classify_result["confidence"] <= 1
        logger.info("✅ test_confidence passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
