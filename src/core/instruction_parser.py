"""
🔍 INSTRUCTION PARSER
Analyse l'input nettoyé et extrait les informations structurées
"""

from typing import Dict, List, Optional, Tuple
from loguru import logger
import re
from enum import Enum

# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class Intent(str, Enum):
    WRITE_CODE = "write_code"
    DEBUG_CODE = "debug_code"
    EXPLAIN = "explain"
    ANALYZE = "analyze"
    REFACTOR = "refactor"
    TEST = "test"
    QUESTION = "question"
    TASK = "task"
    UNKNOWN = "unknown"

class Domain(str, Enum):
    WEB = "web"
    BACKEND = "backend"
    DATA_SCIENCE = "data_science"
    ALGORITHMS = "algorithms"
    DEVOPS = "devops"
    MOBILE = "mobile"
    ML = "machine_learning"
    GENERAL = "general"
    UNKNOWN = "unknown"

class Complexity(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GOLANG = "golang"
    RUST = "rust"
    CPP = "cpp"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    BASH = "bash"
    UNKNOWN = "unknown"

# ============================================================
# KEYWORDS MAPPING
# ============================================================

INTENT_KEYWORDS = {
    Intent.WRITE_CODE: ["write", "create", "make", "build", "generate", "code", "function", "script", "program", "écris", "génère", "crée"],
    Intent.DEBUG_CODE: ["debug", "fix", "error", "bug", "issue", "wrong", "not working", "crash", "corrige", "erreur"],
    Intent.EXPLAIN: ["explain", "what", "how", "why", "describe", "understand", "learn", "explique"],
    Intent.ANALYZE: ["analyze", "review", "check", "examine", "analyse"],
    Intent.REFACTOR: ["refactor", "improve", "optimize", "clean", "simplify"],
    Intent.TEST: ["test", "test case", "unit test", "pytest", "testing"]
}

LANGUAGE_KEYWORDS = {
    Language.PYTHON: ["python", "py", "django", "flask", "pandas", "numpy"],
    Language.JAVASCRIPT: ["javascript", "js", "node", "react", "vue"],
    Language.TYPESCRIPT: ["typescript", "ts"],
    Language.JAVA: ["java", "spring"],
    Language.GOLANG: ["go", "golang"],
    Language.RUST: ["rust"],
    Language.CPP: ["c++", "cpp"],
    Language.SQL: ["sql", "database", "query"],
    Language.HTML: ["html"],
    Language.CSS: ["css", "style"],
    Language.BASH: ["bash", "shell"]
}

DOMAIN_KEYWORDS = {
    Domain.WEB: ["web", "website", "frontend", "html", "css", "react"],
    Domain.BACKEND: ["backend", "api", "server", "database"],
    Domain.DATA_SCIENCE: ["data", "pandas", "numpy", "analysis"],
    Domain.ALGORITHMS: ["algorithm", "sorting", "search", "math", "prime", "fibonacci", "algorithme", "premiers"],
    Domain.DEVOPS: ["deploy", "docker", "kubernetes", "pipeline"],
    Domain.MOBILE: ["mobile", "android", "ios"],
    Domain.ML: ["machine learning", "neural network", "deep learning"]
}

COMPLEXITY_KEYWORDS = {
    Complexity.SIMPLE: ["simple", "easy", "basic", "quick"],
    Complexity.MEDIUM: ["medium", "moderate", "standard", "normal"],
    Complexity.COMPLEX: ["complex", "complicated", "advanced", "hard"],
    Complexity.VERY_COMPLEX: ["very complex", "extremely complex"]
}

# ============================================================
# MAIN PARSER CLASS
# ============================================================

class InstructionParser:
    def __init__(self):
        logger.info("🔧 Initializing Instruction Parser...")
        logger.info("✅ Instruction Parser ready")
    
    def parse(self, instruction: str) -> Dict:
        if not instruction or not instruction.strip():
            return self._empty_result(instruction)
        
        logger.info(f"📝 Parsing instruction: {instruction[:60]}...")
        normalized = instruction.lower().strip()
        
        try:
            intent = self._extract_intent(normalized)
            language = self._extract_language(normalized)
            domain = self._extract_domain(normalized)
            complexity = self._estimate_complexity(normalized)
            requirements = self._extract_requirements(normalized)
            confidence = self._calculate_confidence(intent, language, domain, complexity, requirements)
            
            return {
                "original": instruction,
                "normalized": normalized,
                "intent": intent.value,
                "primary_action": self._intent_to_action(intent),
                "language": language.value if language != Language.UNKNOWN else "none",
                "domain": domain.value,
                "complexity": complexity.value,
                "requirements": requirements,
                "context": self._extract_context(instruction),
                "confidence": round(confidence, 2),
                "success": True
            }
        except Exception as e:
            return self._error_result(instruction, str(e))

    def _extract_intent(self, text: str) -> Intent:
        scores = {intent: sum(1 for kw in keywords if kw in text) for intent, keywords in INTENT_KEYWORDS.items()}
        return max(scores, key=scores.get) if max(scores.values()) > 0 else Intent.UNKNOWN

    def _extract_language(self, text: str) -> Language:
        scores = {lang: sum(1 for kw in keywords if kw in text) for lang, keywords in LANGUAGE_KEYWORDS.items()}
        return max(scores, key=scores.get) if max(scores.values()) > 0 else Language.UNKNOWN

    def _extract_domain(self, text: str) -> Domain:
        scores = {dom: sum(1 for kw in keywords if kw in text) for dom, keywords in DOMAIN_KEYWORDS.items()}
        return max(scores, key=scores.get) if max(scores.values()) > 0 else Domain.GENERAL

    def _estimate_complexity(self, text: str) -> Complexity:
        for complexity, keywords in COMPLEXITY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return complexity
        if len(text) < 50:
            return Complexity.SIMPLE
        if any(w in text for w in ["algorithm", "optimization", "recursive", "architecture", "premiers"]):
            return Complexity.COMPLEX
        return Complexity.MEDIUM

    def _extract_requirements(self, text: str) -> List[str]:
        requirements = []
        patterns = [r"should (.*?)(?:\.|,|$)", r"must (.*?)(?:\.|,|$)", r"with (.*?)(?:\.|,|$)", r"that (.*?)(?:\.|,|$)", r"and (.*?)(?:\.|,|$)]"]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements.extend(matches)
        requirements = [r.strip() for r in requirements if len(r.strip()) > 3]
        if not requirements:
            if "nombre premier" in text or "prime" in text:
                requirements = ["calculate primes", "return list"]
            elif "fonction" in text or "function" in text:
                requirements = ["create function"]
        return list(dict.fromkeys(requirements))

    def _extract_context(self, text: str) -> Dict:
        return {"length": len(text), "word_count": len(text.split()), "has_code_sample": "def " in text, "has_link": "http" in text}

    def _calculate_confidence(self, intent, language, domain, complexity, requirements) -> float:
        score = 0.5
        if intent != Intent.UNKNOWN: score += 0.2
        if language != Language.UNKNOWN: score += 0.15
        if domain != Domain.GENERAL: score += 0.1
        return min(score, 1.0)

    def _intent_to_action(self, intent: Intent) -> str:
        mapping = {Intent.WRITE_CODE: "create_code", Intent.DEBUG_CODE: "debug_code", Intent.EXPLAIN: "explain_concept", Intent.ANALYZE: "analyze_code"}
        return mapping.get(intent, "process_request")

    def _empty_result(self, instruction: str) -> Dict:
        return {"original": instruction, "intent": "unknown", "primary_action": "process_request", "language": "none", "domain": "general", "complexity": "simple", "requirements": [], "context": {}, "confidence": 0.0, "success": False}

    def _error_result(self, instruction: str, error: str) -> Dict:
        return {"original": instruction, "intent": "unknown", "primary_action": "process_request", "language": "none", "domain": "general", "complexity": "simple", "requirements": [], "context": {}, "confidence": 0.0, "success": False, "error": error}

    def batch_parse(self, instructions: List[str]) -> List[Dict]:
        return [self.parse(ins) for ins in instructions]

def demo():
    logger.info("\n" + "="*70 + "\n🔍 INSTRUCTION PARSER - DEMO\n" + "="*70)
    parser = InstructionParser()
    test_instructions = [
        "Write a Python function that calculates prime numbers",
        "Debug this JavaScript code that's not working",
        "Explain how machine learning algorithms work",
        "Refactor this Django backend API",
        "Create a React component for a todo list",
        "Write unit tests for my Python module"
    ]
    for i, ins in enumerate(test_instructions, 1):
        logger.info(f"\n[Test {i}] Input: '{ins}'")
        res = parser.parse(ins)
        logger.info(f"Intent: {res['intent']} | Language: {res['language']} | Domain: {res['domain']} | Confidence: {res['confidence']:.0%}")
    logger.info("\n" + "="*70 + "\n✅ DEMO COMPLETE\n" + "="*70)

if __name__ == "__main__":
    demo()
