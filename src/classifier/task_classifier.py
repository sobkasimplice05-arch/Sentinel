"""📋 TASK CLASSIFIER - Classification des tâches"""

from typing import Dict, List
from loguru import logger
from enum import Enum

class TaskType(str, Enum):
    CODE_IMPLEMENTATION = "code_implementation"
    CODE_DEBUGGING = "code_debugging"
    CODE_OPTIMIZATION = "code_optimization"
    CODE_REFACTORING = "code_refactoring"
    TEST_WRITING = "test_writing"
    DATA_ANALYSIS = "data_analysis"
    EXPLANATION = "explanation"
    SYSTEM_DESIGN = "system_design"
    GENERAL_TASK = "general_task"
    UNKNOWN = "unknown"

class SubCategory(str, Enum):
    SORTING_ALGORITHM = "sorting_algorithm"
    SEARCH_ALGORITHM = "search_algorithm"
    MATHEMATICAL_ALGORITHM = "mathematical_algorithm"
    GRAPH_ALGORITHM = "graph_algorithm"
    FRONTEND_COMPONENT = "frontend_component"
    BACKEND_ENDPOINT = "backend_endpoint"
    MACHINE_LEARNING = "machine_learning"
    UNKNOWN = "unknown"

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

TASK_TYPE_RULES = {
    TaskType.CODE_IMPLEMENTATION: {
        "keywords": ["write", "create", "build", "make", "generate"],
        "intent_match": ["write_code"],
    },
    TaskType.CODE_DEBUGGING: {
        "keywords": ["debug", "fix", "error", "bug", "broken"],
        "intent_match": ["debug_code"],
    },
    TaskType.CODE_OPTIMIZATION: {
        "keywords": ["optimize", "improve", "fast", "performance"],
        "intent_match": ["refactor"],
    },
    TaskType.TEST_WRITING: {
        "keywords": ["test", "pytest", "testing"],
        "intent_match": ["test"],
    },
    TaskType.DATA_ANALYSIS: {
        "keywords": ["analyze", "data", "statistics"],
        "intent_match": ["analyze"],
    },
    TaskType.EXPLANATION: {
        "keywords": ["explain", "what", "how", "why"],
        "intent_match": ["explain"],
    },
}

SUBCATEGORY_RULES = {
    SubCategory.SORTING_ALGORITHM: {"keywords": ["sort", "bubble", "merge"]},
    SubCategory.MATHEMATICAL_ALGORITHM: {"keywords": ["prime", "fibonacci", "math"]},
    SubCategory.FRONTEND_COMPONENT: {"keywords": ["react", "vue", "component"]},
    SubCategory.BACKEND_ENDPOINT: {"keywords": ["api", "endpoint", "rest"]},
    SubCategory.MACHINE_LEARNING: {"keywords": ["machine learning", "ml", "neural"]},
}

class TaskClassifier:
    def __init__(self):
        logger.info("🔧 Initializing Task Classifier...")
        logger.info("✅ Task Classifier ready")
    
    def classify(self, parser_output: Dict) -> Dict:
        if not parser_output or not parser_output.get("success", True):
            return self._error_result(parser_output)
        
        original = parser_output.get("original", "")
        normalized = parser_output.get("normalized", "").lower()
        intent = parser_output.get("intent", "unknown")
        
        logger.info(f"📋 Classifying: {original[:60]}...")
        
        try:
            task_type = self._determine_task_type(intent, normalized)
            sub_category = self._determine_sub_category(normalized)
            priority = self._assess_priority(intent)
            effort = self._estimate_effort(task_type)
            routing_hints = self._get_routing_hints(task_type)
            confidence = self._calculate_confidence(task_type)
            
            result = {
                "success": True,
                "original": original,
                "task_type": task_type.value,
                "sub_category": sub_category.value,
                "priority_level": priority.value,
                "estimated_effort": effort,
                "requires_testing": task_type in [TaskType.CODE_IMPLEMENTATION],
                "requires_documentation": task_type in [TaskType.SYSTEM_DESIGN],
                "routing_hints": routing_hints,
                "confidence": round(confidence, 2),
            }
            
            logger.info(f"✅ Classification complete")
            logger.info(f"   Type: {task_type.value}")
            logger.info(f"   Priority: {priority.value}")
            logger.info(f"   Confidence: {confidence:.0%}")
            
            return result
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return self._error_result(parser_output, str(e))
    
    def _determine_task_type(self, intent: str, text: str) -> TaskType:
        text_lower = text.lower()
        scores = {}
        
        for task_type, rules in TASK_TYPE_RULES.items():
            score = 0
            if intent in rules.get("intent_match", []):
                score += 3
            keywords = rules.get("keywords", [])
            score += sum(1 for kw in keywords if kw in text_lower)
            scores[task_type] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        if intent == "write_code":
            return TaskType.CODE_IMPLEMENTATION
        elif intent == "debug_code":
            return TaskType.CODE_DEBUGGING
        else:
            return TaskType.GENERAL_TASK
    
    def _determine_sub_category(self, text: str) -> SubCategory:
        text_lower = text.lower()
        scores = {}
        
        for subcategory, rules in SUBCATEGORY_RULES.items():
            keywords = rules.get("keywords", [])
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[subcategory] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return SubCategory.UNKNOWN
    
    def _assess_priority(self, intent: str) -> PriorityLevel:
        if intent == "debug_code":
            return PriorityLevel.HIGH
        return PriorityLevel.MEDIUM
    
    def _estimate_effort(self, task_type: TaskType) -> str:
        defaults = {
            TaskType.CODE_IMPLEMENTATION: "1-3 hours",
            TaskType.CODE_DEBUGGING: "1-2 hours",
            TaskType.TEST_WRITING: "1-2 hours",
            TaskType.DATA_ANALYSIS: "2-4 hours",
            TaskType.EXPLANATION: "15-30 minutes",
        }
        return defaults.get(task_type, "Unknown")
    
    def _get_routing_hints(self, task_type: TaskType) -> Dict:
        hints = {
            "best_model": "mistral",
            "secondary_model": "phi",
            "reason": "general task"
        }
        
        if "code" in task_type.value:
            hints["best_model"] = "claude_code"
            hints["reason"] = "Code task"
        elif "data" in task_type.value:
            hints["best_model"] = "deepseek"
            hints["reason"] = "Data analysis"
        
        return hints
    
    def _calculate_confidence(self, task_type: TaskType) -> float:
        return 0.9 if task_type != TaskType.UNKNOWN else 0.5
    
    def _error_result(self, parser_output: Dict, error: str = None) -> Dict:
        return {
            "success": False,
            "original": parser_output.get("original", ""),
            "task_type": TaskType.UNKNOWN.value,
            "sub_category": SubCategory.UNKNOWN.value,
            "priority_level": PriorityLevel.MEDIUM.value,
            "estimated_effort": "Unknown",
            "requires_testing": False,
            "confidence": 0.0,
            "error": error or "Unknown error"
        }
    
    def batch_classify(self, parser_outputs: List[Dict]) -> List[Dict]:
        logger.info(f"Batch classifying {len(parser_outputs)} tasks...")
        results = []
        for output in parser_outputs:
            result = self.classify(output)
            results.append(result)
        logger.info("Batch complete")
        return results

def demo():
    logger.info("\n" + "="*70)
    logger.info("📋 TASK CLASSIFIER - DEMO")
    logger.info("="*70)
    
    from src.core.instruction_parser import InstructionParser
    
    parser = InstructionParser()
    classifier = TaskClassifier()
    
    test_instructions = [
        "Write a Python function for fibonacci",
        "Debug this broken code",
        "Optimize my query",
    ]
    
    for i, instruction in enumerate(test_instructions, 1):
        logger.info(f"\n[{i}] {instruction}")
        parse_result = parser.parse(instruction)
        classify_result = classifier.classify(parse_result)
        logger.info(f"    Type: {classify_result['task_type']}")
        logger.info(f"    Priority: {classify_result['priority_level']}")
        logger.info(f"    Model: {classify_result['routing_hints']['best_model']}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ DEMO COMPLETE\n")

if __name__ == "__main__":
    demo()
