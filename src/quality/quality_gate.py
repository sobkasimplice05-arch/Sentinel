"""🛡️ QUALITY GATE - 5 vérificateurs
Syntax, Logic, Security, Hallucination, Completeness
"""

from typing import Dict, List
from loguru import logger
import re
import json

class SyntaxChecker:
    """Vérifie la syntaxe du code"""
    
    def check(self, response: str, language: str = None) -> Dict:
        logger.info("🔍 Checking syntax...")
        
        if not response or not response.strip():
            return {"valid": False, "score": 0, "issues": ["Empty response"]}
        
        # Pour Python
        if language == "python" or "def " in response or "import " in response:
            try:
                compile(response, '<string>', 'exec')
                logger.info("   ✅ Valid syntax")
                return {"valid": True, "score": 1.0, "issues": []}
            except SyntaxError as e:
                logger.warning(f"   ⚠️ Syntax error: {e}")
                return {"valid": False, "score": 0.3, "issues": [str(e)]}
        
        # Pour d'autres: vérifier équilibre parenthèses
        if response.count("(") == response.count(")") and \
           response.count("{") == response.count("}") and \
           response.count("[") == response.count("]"):
            return {"valid": True, "score": 0.9, "issues": []}
        
        return {"valid": True, "score": 0.7, "issues": ["Possible bracket mismatch"]}

class LogicValidator:
    """Valide la logique du code"""
    
    def check(self, response: str) -> Dict:
        logger.info("🔍 Checking logic...")
        
        score = 0.8
        issues = []
        
        # Check for common logic issues
        if "TODO" in response or "FIXME" in response:
            score -= 0.2
            issues.append("Contains TODO/FIXME")
        
        if "undefined" in response.lower() or "null" in response.lower():
            score -= 0.1
            issues.append("Potential undefined variables")
        
        # Check for return statements
        if "def " in response and "return" not in response:
            score -= 0.15
            issues.append("Function without return statement")
        
        logger.info(f"   Logic score: {score:.1%}")
        return {"valid": score >= 0.6, "score": max(0, score), "issues": issues}

class SecurityAnalyzer:
    """Analyse les failles de sécurité"""
    
    def check(self, response: str) -> Dict:
        logger.info("🔍 Checking security...")
        
        score = 1.0
        issues = []
        
        dangerous_patterns = [
            (r"\beval\(", "Use of eval() is dangerous"),
            (r"\bexec\(", "Use of exec() is dangerous"),
            (r"\b__import__\b", "Dynamic import detected"),
            (r"\bos\.system\(", "Subprocess or shell execution risk"),
            (r"\bsubprocess\.Popen\(", "Subprocess Popen detected"),
            (r"\bsubprocess\.call\(", "Subprocess call without safety checks"),
            (r"\bopen\(.*?['\"]w['\"]", "Potential file overwrite or injection via open()"),
            (r"\brequests\.(get|post|put|delete|patch)\(", "External request detected"),
            (r"\byaml\.load\(", "Unsafe YAML loading"),
            (r"\bpickle\.loads\(", "Unsafe pickle deserialization"),
        ]
        
        for pattern, issue in dangerous_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                score -= 0.25
                issues.append(issue)
        
        sql_patterns = [
            (r"\bSELECT\b.*\bFROM\b", "SQL query detected"),
            (r"\bINSERT\b.*\bINTO\b", "SQL query detected"),
            (r"\bUPDATE\b.*\bSET\b", "SQL query detected"),
            (r"\bDELETE\b.*\bFROM\b", "SQL query detected"),
            (r"\bDROP\b.*\bTABLE\b", "SQL injection risk"),
            (r"['\"]\s*;\s*DROP\s+TABLE", "Possible SQL injection"),
        ]
        
        for pattern, issue in sql_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                score -= 0.2
                issues.append(issue)
        
        secret_patterns = [
            (r"\bpassword\b\s*=\s*['\"].*['\"]", "Hardcoded password"),
            (r"\bapi[_-]?key\b\s*=\s*['\"].*['\"]", "Hardcoded API key"),
            (r"\bsecret\b\s*=\s*['\"].*['\"]", "Hardcoded secret"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "Email address detected"),
        ]
        
        for pattern, issue in secret_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                score -= 0.2
                issues.append(issue)
        
        logger.info(f"   Security score: {score:.1%}")
        return {"valid": score >= 0.7, "score": max(0, score), "issues": issues}

class HallucinationDetector:
    """Détecte les hallucinations (fausses informations)"""
    
    def check(self, response: str) -> Dict:
        logger.info("🔍 Checking for hallucinations...")
        
        score = 0.9
        issues = []
        
        # Check for uncertainty markers
        uncertain_phrases = [
            "I think",
            "probably",
            "might be",
            "could be",
            "not sure",
            "I guess"
        ]
        
        uncertain_count = sum(1 for phrase in uncertain_phrases if phrase.lower() in response.lower())
        if uncertain_count > 2:
            score -= 0.15
            issues.append(f"High uncertainty ({uncertain_count} uncertain phrases)")
        
        # Check for made-up information patterns
        if re.search(r"[A-Z][a-z]+ [0-9]{4}", response):  # Company + year pattern
            score -= 0.05
        
        logger.info(f"   Hallucination score: {score:.1%}")
        return {"valid": score >= 0.6, "score": max(0, score), "issues": issues}

class CompletenessChecker:
    """Vérifie que la réponse est complète"""
    
    def check(self, response: str, task_type: str = None) -> Dict:
        logger.info("🔍 Checking completeness...")
        
        score = 1.0
        issues = []
        
        # Check minimum length
        if len(response.strip()) < 20:
            score -= 0.4
            issues.append("Response too short")
        
        # For code tasks
        if task_type == "code_implementation":
            if "def " in response or "class " in response:
                if "return" not in response and "print" not in response:
                    score -= 0.2
                    issues.append("Code doesn't produce output")
            
            if response.count("\n") < 2:
                score -= 0.1
                issues.append("Code seems incomplete")
        
        # Check for incomplete sentences
        if response.endswith(",") or response.endswith("and") or response.endswith("or"):
            score -= 0.15
            issues.append("Incomplete sentence at end")
        
        logger.info(f"   Completeness score: {score:.1%}")
        return {"valid": score >= 0.6, "score": max(0, score), "issues": issues}

class QualityGate:
    """Le portail de qualité - valide tout avant de retourner"""
    
    def __init__(self):
        logger.info("🛡️ Initializing Quality Gate...")
        self.syntax_checker = SyntaxChecker()
        self.logic_validator = LogicValidator()
        self.security_analyzer = SecurityAnalyzer()
        self.hallucination_detector = HallucinationDetector()
        self.completeness_checker = CompletenessChecker()
        logger.info("✅ Quality Gate ready (5 checkers)")
    
    def evaluate(self, response: str, task_type: str = None, language: str = None) -> Dict:
        """Évalue la réponse complètement"""
        
        logger.info(f"🛡️ Quality Gate evaluating response...")
        
        # Run all checkers
        syntax_result = self.syntax_checker.check(response, language)
        logic_result = self.logic_validator.check(response)
        security_result = self.security_analyzer.check(response)
        hallucination_result = self.hallucination_detector.check(response)
        completeness_result = self.completeness_checker.check(response, task_type)
        
        # Calculate overall score
        weights = {
            "syntax": 0.2,
            "logic": 0.2,
            "security": 0.25,
            "hallucination": 0.15,
            "completeness": 0.2,
        }
        
        overall_score = (
            syntax_result["score"] * weights["syntax"] +
            logic_result["score"] * weights["logic"] +
            security_result["score"] * weights["security"] +
            hallucination_result["score"] * weights["hallucination"] +
            completeness_result["score"] * weights["completeness"]
        )
        
        result = {
            "success": overall_score >= 0.75,
            "overall_score": round(overall_score, 2),
            "status": "PASS" if overall_score >= 0.75 else "REVIEW",
            "checkers": {
                "syntax": syntax_result,
                "logic": logic_result,
                "security": security_result,
                "hallucination": hallucination_result,
                "completeness": completeness_result,
            },
            "all_issues": self._collect_issues([
                syntax_result,
                logic_result,
                security_result,
                hallucination_result,
                completeness_result,
            ])
        }
        
        logger.info(f"✅ Gate evaluation complete")
        logger.info(f"   Overall score: {overall_score:.0%}")
        logger.info(f"   Status: {result['status']}")
        
        return result
    
    def _collect_issues(self, results: List[Dict]) -> List[str]:
        """Collecte tous les problèmes"""
        issues = []
        for result in results:
            issues.extend(result.get("issues", []))
        return issues

def demo():
    logger.info("\n" + "="*70)
    logger.info("🛡️ QUALITY GATE - DEMO")
    logger.info("="*70 + "\n")
    
    gate = QualityGate()
    
    test_responses = [
        "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "This is a good response",
        "eval('dangerous code')",
        "password = 'secret123'",
    ]
    
    for i, response in enumerate(test_responses, 1):
        logger.info(f"\n[Test {i}]")
        result = gate.evaluate(response, task_type="code_implementation")
        logger.info(f"Score: {result['overall_score']:.0%}")
        logger.info(f"Status: {result['status']}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ QUALITY GATE WORKING\n")

if __name__ == "__main__":
    demo()

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24

# Auto-enhanced security signature: Sentinel Ouroboros H24
