from typing import Dict, List, Optional, Set, Tuple
from loguru import logger
from enum import Enum
import json


# ============================================================
# ENUMS - TASK TYPES
# ============================================================

class TaskType(str, Enum):
    """Types de tâches principaux"""
    
    # Code-related
    CODE_IMPLEMENTATION = "code_implementation"
    CODE_DEBUGGING = "code_debugging"
    CODE_OPTIMIZATION = "code_optimization"
    CODE_REFACTORING = "code_refactoring"
    CODE_REVIEW = "code_review"
    TEST_WRITING = "test_writing"
    
    # Data-related
    DATA_ANALYSIS = "data_analysis"
    DATA_VISUALIZATION = "data_visualization"
    DATA_PROCESSING = "data_processing"
    
    # Architecture
    SYSTEM_DESIGN = "system_design"
    DATABASE_DESIGN = "database_design"
    API_DESIGN = "api_design"
    
    # Learning
    EXPLANATION = "explanation"
    TUTORIAL = "tutorial"
    DOCUMENTATION = "documentation"
    
    # Misc
    QUESTION_ANSWERING = "question_answering"
    GENERAL_TASK = "general_task"
    UNKNOWN = "unknown"


class SubCategory(str, Enum):
    """Sous-catégories"""
    
    # Algorithms
    SORTING_ALGORITHM = "sorting_algorithm"
    SEARCH_ALGORITHM = "search_algorithm"
    MATHEMATICAL_ALGORITHM = "mathematical_algorithm"
    STRING_ALGORITHM = "string_algorithm"
    GRAPH_ALGORITHM = "graph_algorithm"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    
    # Web
    FRONTEND_COMPONENT = "frontend_component"
    BACKEND_ENDPOINT = "backend_endpoint"
    FULL_STACK_APP = "full_stack_app"
    API_REST = "api_rest"
    
    # Data
    DATA_CLEANING = "data_cleaning"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    MACHINE_LEARNING = "machine_learning"
    VISUALIZATION = "visualization"
    
    # DevOps
    DEPLOYMENT = "deployment"
    INFRASTRUCTURE = "infrastructure"
    CI_CD = "ci_cd"
    CONTAINERIZATION = "containerization"
    
    # Database
    QUERY_OPTIMIZATION = "query_optimization"
    SCHEMA_DESIGN = "schema_design"
    MIGRATION = "migration"
    INDEXING = "indexing"
    
    UNKNOWN = "unknown"


class PriorityLevel(str, Enum):
    """Niveaux de priorité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# CLASSIFICATION RULES
# ============================================================

TASK_TYPE_RULES = {
    TaskType.CODE_IMPLEMENTATION: {
        "keywords": ["write", "create", "build", "make", "generate", "implement"],
        "intent_match": ["write_code"],
        "domain_match": ["algorithms", "web", "backend", "general"],
    },
    TaskType.CODE_DEBUGGING: {
        "keywords": ["debug", "fix", "error", "bug", "broken", "not working", "crash"],
        "intent_match": ["debug_code"],
    },
    TaskType.CODE_OPTIMIZATION: {
        "keywords": ["optimize", "improve", "fast", "efficient", "performance", "speed"],
        "intent_match": ["refactor"],
    },
    TaskType.CODE_REFACTORING: {
        "keywords": ["refactor", "clean", "reorganize", "simplify", "improve"],
        "intent_match": ["refactor"],
    },
    TaskType.TEST_WRITING: {
        "keywords": ["test", "test case", "unit test", "testing", "pytest"],
        "intent_match": ["test"],
    },
    TaskType.DATA_ANALYSIS: {
        "keywords": ["analyze", "data", "statistics", "analyze", "explore"],
        "intent_match": ["analyze"],
        "domain_match": ["data_science"],
    },
    TaskType.EXPLANATION: {
        "keywords": ["explain", "what", "how", "why", "understand", "learn"],
        "intent_match": ["explain"],
    },
}

SUBCATEGORY_RULES = {
    SubCategory.SORTING_ALGORITHM: {
        "keywords": ["sort", "bubble sort", "merge sort", "quick sort"],
    },
    SubCategory.SEARCH_ALGORITHM: {
        "keywords": ["search", "binary search", "linear search", "find"],
    },
    SubCategory.MATHEMATICAL_ALGORITHM: {
        "keywords": ["prime", "fibonacci", "factorial", "math", "calculate"],
    },
    SubCategory.GRAPH_ALGORITHM: {
        "keywords": ["graph", "tree", "node", "edge", "path"],
    },
    SubCategory.DYNAMIC_PROGRAMMING: {
        "keywords": ["dynamic", "memoization", "recursion", "cache"],
    },
    SubCategory.FRONTEND_COMPONENT: {
        "keywords": ["react", "vue", "angular", "component", "ui", "button"],
    },
    SubCategory.BACKEND_ENDPOINT: {
        "keywords": ["api", "endpoint", "route", "rest", "flask", "django"],
    },
    SubCategory.MACHINE_LEARNING: {
        "keywords": ["machine learning", "ml", "neural", "model", "training"],
    },
}

EFFORT_ESTIMATION = {
    ("simple", "code_implementation"): "15-30 minutes",
    ("simple", "explanation"): "5-10 minutes",
    ("simple", "question_answering"): "5-10 minutes",
    
    ("medium", "code_implementation"): "1-3 hours",
    ("medium", "code_debugging"): "1-2 hours",
    ("medium", "test_writing"): "1-2 hours",
    
    ("complex", "code_implementation"): "4-8 hours",
    ("complex", "system_design"): "4-8 hours",
    ("complex", "data_analysis"): "3-6 hours",
    
    ("very_complex", "system_design"): "2-5 days",
    ("very_complex", "machine_learning"): "1-2 weeks",
}


# ============================================================
# MAIN CLASSIFIER CLASS
# ============================================================

class TaskClassifier:
    """
    Classifie précisément les tâches après parsing
    
    Stratégie:
    1. Determine task type (code/data/learning?)
    2. Find sub-category (algorithm/component/etc?)
    3. Assess priority (urgent?)
    4. Estimate effort (combien de temps?)
    5. Suggest best model (qui pour cette tâche?)
    """
    
    def __init__(self):
        """Initialise le classifier"""
        logger.info("🔧 Initializing Task Classifier...")
        self.logger = logger
        logger.info("✅ Task Classifier ready")
    
    def classify(self, parser_output: Dict) -> Dict:
        """
        Classifie une tâche basée sur le parser output
        
        Args:
            parser_output: Output du InstructionParser
        
        Returns:
            Dict avec classification détaillée
        """
        
        if not parser_output or not parser_output.get("success", True):
            logger.warning("Invalid parser output")
            return self._error_result(parser_output)
        
        original = parser_output.get("original", "")
        normalized = parser_output.get("normalized", "")
        
        logger.info(f"📋 Classifying task: {original[:60]}...")
        
        try:
            # Extract base info from parser
            intent = parser_output.get("intent", "unknown")
            language = parser_output.get("language")
            domain = parser_output.get("domain", "general")
            complexity = parser_output.get("complexity", "medium")
            requirements = parser_output.get("requirements", [])
            
            # Determine task type
            task_type = self._determine_task_type(
                intent, language, domain, normalized, requirements
            )
            
            # Determine sub-category
            sub_category = self._determine_sub_category(
                task_type, language, domain, normalized, requirements
            )
            
            # Assess priority
            priority = self._assess_priority(
                complexity, intent, requirements
            )
            
            # Estimate effort
            effort = self._estimate_effort(complexity, task_type)
            
            # Determine requirements
            req_testing = self._requires_testing(task_type, language)
            req_docs = self._requires_documentation(task_type, complexity)
            
            # Get routing hints
            routing_hints = self._get_routing_hints(
                task_type, language, complexity, domain
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                task_type, sub_category, priority
            )
            
            result = {
                "success": True,
                "original": original,
                
                # Classification
                "task_type": task_type.value,
                "sub_category": sub_category.value,
                "priority_level": priority.value,
                
                # Details
                "estimated_effort": effort,
                "requires_testing": req_testing,
                "requires_documentation": req_docs,
                
                # Metadata
                "language": language,
                "domain": domain,
                "complexity": complexity,
                "requirements": requirements,
                
                # Routing
                "routing_hints": routing_hints,
                
                # Confidence
                "confidence": round(confidence, 2),
            }
            
            logger.info(f"✅ Classification complete")
            logger.info(f"   Task Type: {task_type.value}")
            logger.info(f"   Sub Category: {sub_category.value}")
            logger.info(f"   Priority: {priority.value}")
            logger.info(f"   Effort: {effort}")
            logger.info(f"   Confidence: {confidence:.0%}")
            
            return result
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"❌ Classification error: {e}")
            return self._error_result(parser_output, str(e))
    
    def _determine_task_type(
        self,
        intent: str,
        language: Optional[str],
        domain: str,
        text: str,
        requirements: List[str]
    ) -> TaskType:
        """Détermine le type de tâche"""
        
        text_lower = text.lower()
        
        # Score each task type
        scores = {}
        
        for task_type, rules in TASK_TYPE_RULES.items():
            score = 0
            
            # Check intent match
            if intent in rules.get("intent_match", []):
                score += 3
            
            # Check keywords
            keywords = rules.get("keywords", [])
            score += sum(1 for kw in keywords if kw in text_lower)
            
            # Check domain match
            if domain in rules.get("domain_match", []):
                score += 2
            
            scores[task_type] = score
        
        # Return best match
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # Default based on intent
        if intent == "write_code":
            return TaskType.CODE_IMPLEMENTATION
        elif intent == "debug_code":
            return TaskType.CODE_DEBUGGING
        elif intent == "explain":
            return TaskType.EXPLANATION
        elif intent == "analyze":
            return TaskType.DATA_ANALYSIS
        else:
            return TaskType.GENERAL_TASK
    
    def _determine_sub_category(
        self,
        task_type: TaskType,
        language: Optional[str],
        domain: str,
        text: str,
        requirements: List[str]
    ) -> SubCategory:
        """Détermine la sous-catégorie"""
        
        text_lower = text.lower()
        scores = {}
        
        # Score each subcategory
        for subcategory, rules in SUBCATEGORY_RULES.items():
            keywords = rules.get("keywords", [])
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[subcategory] = score
        
        # Also check requirements
        for req in requirements:
            for subcategory, rules in SUBCATEGORY_RULES.items():
                keywords = rules.get("keywords", [])
                if any(kw in req.lower() for kw in keywords):
                    scores[subcategory] = scores.get(subcategory, 0) + 2
        
        # Return best match
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return SubCategory.UNKNOWN
    
    def _assess_priority(
        self,
        complexity: str,
        intent: str,
        requirements: List[str]
    ) -> PriorityLevel:
        """Évalue la priorité"""
        
        # Complexité élevée → priorité élevée
        if complexity in ["complex", "very_complex"]:
            return PriorityLevel.HIGH
        
        # Mots-clés urgents
        urgent_keywords = ["urgent", "asap", "critical", "immediately", "now"]
        if any(kw in " ".join(requirements).lower() for kw in urgent_keywords):
            return PriorityLevel.CRITICAL
        
        # Debug/fix → priorité moyenne-élevée
        if intent == "debug_code":
            return PriorityLevel.HIGH
        
        # Default
        return PriorityLevel.MEDIUM
    
    def _estimate_effort(self, complexity: str, task_type: TaskType) -> str:
        """Estime l'effort requis"""
        
        key = (complexity, task_type.value)
        
        # Look up in mapping
        if key in EFFORT_ESTIMATION:
            return EFFORT_ESTIMATION[key]
        
        # Default estimates
        defaults = {
            "simple": "15-30 minutes",
            "medium": "1-3 hours",
            "complex": "4-8 hours",
            "very_complex": "1-2 days",
        }
        
        return defaults.get(complexity, "Unknown")
    
    def _requires_testing(self, task_type: TaskType, language: Optional[str]) -> bool:
        """Détermine si des tests sont nécessaires"""
        
        # Code needs testing
        if task_type in [
            TaskType.CODE_IMPLEMENTATION,
            TaskType.CODE_OPTIMIZATION,
            TaskType.CODE_REFACTORING,
        ]:
            return True
        
        # Algorithms need testing
        if "algorithm" in task_type.value.lower():
            return True
        
        return False
    
    def _requires_documentation(self, task_type: TaskType, complexity: str) -> bool:
        """Détermine si de la documentation est nécessaire"""
        
        # Always document complex tasks
        if complexity in ["complex", "very_complex"]:
            return True
        
        # Document public APIs
        if "api" in task_type.value.lower():
            return True
        
        # Document system designs
        if task_type == TaskType.SYSTEM_DESIGN:
            return True
        
        return False
    
    def _get_routing_hints(
        self,
        task_type: TaskType,
        language: Optional[str],
        complexity: str,
        domain: str
    ) -> Dict:
        """Fournit des hints pour le routage des modèles"""
        
        hints = {
            "best_model": "mistral",  # default
            "secondary_model": "phi",
            "reason": "general task"
        }
        
        # Code tasks → Claude Code
        if "code" in task_type.value.lower():
            hints["best_model"] = "claude_code"
            hints["reason"] = "Needs code generation/modification"
        
        # Algorithm tasks → Claude Code or DeepSeek
        if "algorithm" in task_type.value.lower():
            hints["best_model"] = "claude_code"
            hints["secondary_model"] = "deepseek"
            hints["reason"] = "Requires algorithmic thinking"
        
        # Data analysis → DeepSeek or Mistral
        if "data" in task_type.value.lower():
            hints["best_model"] = "deepseek"
            hints["secondary_model"] = "mistral"
            hints["reason"] = "Needs analytical reasoning"
        
        # Explanation tasks → Claude Code or Mistral
        if task_type == TaskType.EXPLANATION:
            hints["best_model"] = "mistral"
            hints["secondary_model"] = "claude_code"
            hints["reason"] = "Needs clear explanation"
        
        # System design → Claude Code (best for architecture)
        if task_type == TaskType.SYSTEM_DESIGN:
            hints["best_model"] = "claude_code"
            hints["reason"] = "Needs architectural thinking"
        
        # Complex tasks → DeepSeek (chain-of-thought)
        if complexity == "very_complex":
            hints["best_model"] = "deepseek"
            hints["reason"] = "Needs extended reasoning"
        
        return hints
    
    def _calculate_confidence(
        self,
        task_type: TaskType,
        sub_category: SubCategory,
        priority: PriorityLevel
    ) -> float:
        """Calcule la confiance de la classification"""
        
        confidence = 0.75  # baseline
        
        # Si task type est déterminé → +0.1
        if task_type != TaskType.UNKNOWN:
            confidence += 0.1
        
        # Si sub-category est trouvée → +0.1
        if sub_category != SubCategory.UNKNOWN:
            confidence += 0.1
        
        # Cap at 1.0
        return min(1.0, confidence)
    
    def _error_result(self, parser_output: Dict, error: str = None) -> Dict:
        """Résultat en cas d'erreur"""
        
        return {
            "success": False,
            "original": parser_output.get("original", ""),
            "task_type": TaskType.UNKNOWN.value,
            "sub_category": SubCategory.UNKNOWN.value,
            "priority_level": PriorityLevel.MEDIUM.value,
            "estimated_effort": "Unknown",
            "requires_testing": False,
            "requires_documentation": False,
            "routing_hints": {"best_model": "mistral"},
            "confidence": 0.0,
            "error": error or "Unknown classification error"
        }
    
    def batch_classify(self, parser_outputs: List[Dict]) -> List[Dict]:
        """Classifie plusieurs tâches"""
        
        logger.info(f"🔄 Batch classifying {len(parser_outputs)} tasks...")
        
        results = []
        for i, output in enumerate(parser_outputs):
            logger.info(f"   [{i+1}/{len(parser_outputs)}]")
            result = self.classify(output)
            results.append(result)
        
        logger.info("✅ Batch classification complete")
        return results


# ============================================================
# DEMO
# ============================================================

def demo():
    """Demo du classifier"""
    
    logger.info("\n" + "="*70)
    logger.info("📋 TASK CLASSIFIER - DEMO")
    logger.info("="*70 + "\n")
    
    # Import parser for complete demo
    from src.core.instruction_parser import InstructionParser
    
    parser = InstructionParser()
    classifier = TaskClassifier()
    
    test_instructions = [
        "Write a Python function that calculates prime numbers",
        "Debug this broken JavaScript code",
        "Optimize my slow SQL query",
        "Refactor my Django REST API",
        "Create a React component for authentication",
        "Write unit tests for my module",
        "Analyze this dataset with pandas",
        "Design a system architecture for scaling",
        "Explain how machine learning works",
    ]
    
    for i, instruction in enumerate(test_instructions, 1):
        logger.info(f"\n[Task {i}]")
        logger.info(f"Instruction: '{instruction}'")
        
        # Parse
        parse_result = parser.parse(instruction)
        
        # Classify
        classify_result = classifier.classify(parse_result)
        
        logger.info(f"Task Type:    {classify_result['task_type']}")
        logger.info(f"Sub Category: {classify_result['sub_category']}")
        logger.info(f"Priority:     {classify_result['priority_level']}")
        logger.info(f"Effort:       {classify_result['estimated_effort']}")
        logger.info(f"Best Model:   {classify_result['routing_hints']['best_model']}")
        logger.info(f"Confidence:   {classify_result['confidence']:.0%}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ DEMO COMPLETE")
    logger.info("="*70 + "\n")


if __name__ == "__main__":
    demo()
