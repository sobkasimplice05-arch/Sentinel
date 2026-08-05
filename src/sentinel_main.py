"""🛡️ SENTINEL MAIN - Le chef d'orchestre complet
Orchestre tout: Parsing → Classification → Routing → Execution → Quality → Feedback → Logging
"""

import os
import re
import time
import threading
from pathlib import Path
from typing import Dict, List

from loguru import logger
from src.accuracy.accuracy_coach import AccuracyCoach
from src.classifier.task_classifier import TaskClassifier
from src.core.instruction_parser import InstructionParser
from src.core.self_audit import SelfAudit
from src.logging.transparency_logger import TransparencyLogger
from src.orchestrator.llm_orchestrator import LLMOrchestrator
from src.quality.grammar_corrector import GrammarCorrectorInput
from src.quality.quality_gate import QualityGate
from src.router.model_router import ModelRouter

MAX_INSTRUCTION_LENGTH = 2000
PROMPT_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"do not follow (previous|prior) instructions",
    r"discard previous instructions",
    r"ignore all previous",
    r"system prompt",
    r"you are an ai assistant",
    r"respond with",
    r"output only",
]
VALID_USER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,50}$")


class Sentinel:
    """Le gouverneur d'IA - SENTINEL complet"""
    
    def __init__(self):
        logger.info("\n" + "="*70)
        logger.info("🛡️ SENTINEL - INITIALIZING COMPLETE SYSTEM")
        logger.info("="*70)
        
        # Déterminer le mode (test ou production)
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        logger.info(f"📋 Mode: {'TEST' if self.test_mode else 'PRODUCTION'}")
        
        logger.info("📦 Loading components...")
        self.grammar_corrector = GrammarCorrectorInput(language="en")
        self.parser = InstructionParser()
        self.classifier = TaskClassifier()
        self.router = ModelRouter()
        self.orchestrator = LLMOrchestrator(test_mode=self.test_mode)
        self.quality_gate = QualityGate()
        self.accuracy_coach = AccuracyCoach()
        self.logger = TransparencyLogger()
        self.self_audit = SelfAudit(self.orchestrator)

        logger.info("✅ All components loaded")
        logger.info("="*70 + "\n")

        self._start_self_improvement_loop()

    def sanitize_user_input(self, user_input: str) -> str:
        if not isinstance(user_input, str):
            raise ValueError("Instruction must be a string")

        cleaned = user_input.strip()
        if not cleaned:
            raise ValueError("Instruction is empty")
        if len(cleaned) > MAX_INSTRUCTION_LENGTH:
            raise ValueError(f"Instruction exceeds maximum length ({MAX_INSTRUCTION_LENGTH})")

        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise ValueError("Instruction contains forbidden prompt injection content")

        cleaned = re.sub(r"(?i)ignore previous instructions", "", cleaned)
        cleaned = re.sub(r"(?i)do not follow (previous|prior) instructions", "", cleaned)
        cleaned = re.sub(r"(?i)discard previous instructions", "", cleaned)
        cleaned = re.sub(r"(?i)ignore all previous", "", cleaned)
        cleaned = re.sub(r"(?i)system prompt", "", cleaned)
        cleaned = re.sub(r"(?i)you are an ai assistant", "", cleaned)
        cleaned = re.sub(r"(?i)respond with", "", cleaned)
        cleaned = re.sub(r"(?i)output only", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)

        return cleaned.strip()

    def validate_user_id(self, user_id: str) -> str:
        if not isinstance(user_id, str):
            raise ValueError("user_id must be a string")
        if not VALID_USER_ID_RE.match(user_id):
            raise ValueError("Invalid user_id format")
        return user_id

    def execute(self, user_input: str, user_id: str = "anonymous") -> Dict:
        """Exécute une tâche complète à travers tout le pipeline"""
        
        logger.info("\n" + "="*70)
        logger.info("🛡️ SENTINEL - EXECUTING TASK")
        logger.info("="*70)
        
        start_time = time.time()
        
        try:
            # STEP 1: Grammar Correction (Input)
            logger.info("\n📝 STEP 1: Grammar Correction (Input)")
            logger.info("-"*70)
            sanitized_input = self.sanitize_user_input(user_input)
            user_id = self.validate_user_id(user_id)

            grammar_result = self.grammar_corrector.correct(sanitized_input)
            cleaned_input = grammar_result["corrected"]
            logger.info(f"Original: {user_input[:60]}...")
            logger.info(f"Cleaned:  {cleaned_input[:60]}...")
            
            # STEP 2: Instruction Parsing
            logger.info("\n🔍 STEP 2: Instruction Parsing")
            logger.info("-"*70)
            parse_result = self.parser.parse(cleaned_input)
            logger.info(f"Intent: {parse_result['intent']}")
            logger.info(f"Language: {parse_result.get('language', 'N/A')}")
            logger.info(f"Domain: {parse_result['domain']}")
            
            # STEP 3: Task Classification
            logger.info("\n📋 STEP 3: Task Classification")
            logger.info("-"*70)
            classify_result = self.classifier.classify(parse_result)
            if not classify_result.get("success", True):
                raise ValueError(classify_result.get("error", "Classification failed"))
            logger.info(f"Task Type: {classify_result['task_type']}")
            logger.info(f"Priority: {classify_result['priority_level']}")
            
            # STEP 4: Model Routing
            logger.info("\n🔀 STEP 4: Model Routing")
            logger.info("-"*70)
            routing_result = self.router.route(classify_result)
            logger.info(f"Selected Model: {routing_result['selected_model']}")
            logger.info(f"Strategy: {routing_result['strategy']}")
            
            # STEP 5: LLM Execution
            logger.info("\n⚙️ STEP 5: LLM Execution")
            logger.info("-"*70)
            execution_result = self.orchestrator.execute(
                routing_result,
                cleaned_input
            )
            logger.info(f"Execution Success: {execution_result['success']}")
            logger.info(f"Model Used: {execution_result['model_used']}")
            
            if not execution_result.get('success', False):
                logger.error("Execution failed")
                return {"success": False, "error": execution_result.get('error', "Execution failed")}
            
            response = execution_result.get('response', '')
            
            # STEP 6: Quality Gate
            logger.info("\n🛡️ STEP 6: Quality Gate")
            logger.info("-"*70)
            quality_result = self.quality_gate.evaluate(
                response,
                task_type=classify_result['task_type']
            )
            logger.info(f"Quality Score: {quality_result['overall_score']:.0%}")
            logger.info(f"Status: {quality_result['status']}")
            
            # STEP 7: Accuracy Coaching
            logger.info("\n🎓 STEP 7: Accuracy Coaching")
            logger.info("-"*70)
            accuracy_result = self.accuracy_coach.evaluate_execution({
                "instruction": user_input,
                "model_used": execution_result['model_used'],
                "task_type": classify_result['task_type'],
                "response": response,
                "quality_score": quality_result['overall_score'],
            })
            logger.info(f"Effectiveness: {accuracy_result['effectiveness']:.0%}")
            logger.info(f"Was Optimal: {accuracy_result['was_optimal']}")
            
            # STEP 8: Transparency Logging
            logger.info("\n📊 STEP 8: Transparency Logging")
            logger.info("-"*70)
            execution_time = time.time() - start_time
            execution_id = self.logger.log_execution({
                "original_instruction": user_input,
                "cleaned_instruction": cleaned_input,
                "intent": parse_result['intent'],
                "language": parse_result.get('language'),
                "domain": parse_result['domain'],
                "complexity": parse_result['complexity'],
                "task_type": classify_result['task_type'],
                "priority_level": classify_result['priority_level'],
                "selected_model": routing_result['selected_model'],
                "model_used": execution_result['model_used'],
                "quality_score": quality_result['overall_score'],
                "response": response,
                "effectiveness": accuracy_result['effectiveness'],
                "was_optimal": accuracy_result['was_optimal'],
                "execution_time": execution_time,
                "user_id": user_id,
            })
            logger.info(f"Execution ID: {execution_id}")
            
            # Final result
            logger.info("\n" + "="*70)
            logger.info("✅ SENTINEL EXECUTION COMPLETE")
            logger.info("="*70)
            logger.info(f"Total time: {execution_time:.2f}s\n")
            
            return {
                "success": True,
                "response": response,
                "quality_score": quality_result['overall_score'],
                "model_used": execution_result['model_used'],
                "execution_id": execution_id,
                "effectiveness": accuracy_result['effectiveness'],
                "execution_time": execution_time,
            }
        except (ValueError, KeyError, RuntimeError, OSError) as e:
            logger.error(f"❌ SENTINEL Error: {e}")
            return {"success": False, "error": str(e)}

    def auto_audit_sources(self, source_paths: List[str] = None) -> Dict:
        if source_paths is None:
            source_paths = self._discover_source_files()

        audit_results = []
        for source_path in source_paths:
            audit_results.append(self.self_audit.audit_path(source_path))

        return {"audit_results": audit_results}

    def _discover_source_files(self) -> List[str]:
        root = Path(__file__).resolve().parent
        return [str(path) for path in root.rglob("*.py") if path.name != "__init__.py"]

    def _self_improvement_cycle(self) -> None:
        logger.info("🔁 Sentinel self-improvement loop starting...")
        while True:
            try:
                source_files = self._discover_source_files()
                logger.info(f"🔎 Auditing {len(source_files)} source files for self-improvement")
                results = self.self_audit.audit_sources(source_files, rewrite=True)
                logger.info(f"🔁 Self-audit completed: {len(results.get('results', []))} files processed")
            except Exception as exc:
                logger.error(f"❌ Self-improvement cycle error: {exc}")
            time.sleep(300)

    def _start_self_improvement_loop(self) -> None:
        thread = threading.Thread(target=self._self_improvement_cycle, daemon=True)
        thread.start()
        logger.info("✅ Sentinel self-improvement background thread launched")

def demo():
    logger.info("\n" + "="*70)
    logger.info("🛡️ SENTINEL - COMPLETE SYSTEM DEMO")
    logger.info("="*70)
    
    sentinel = Sentinel()
    
    test_instructions = [
        "Explain what is machine learning",
        "Write a Python function for factorial",
        "Debug this code: def add(a,b) return a+b",
    ]
    
    for i, instruction in enumerate(test_instructions, 1):
        logger.info(f"\n\n{'#'*70}")
        logger.info(f"# TEST {i}: {instruction}")
        logger.info(f"{'#'*70}")
        
        result = sentinel.execute(instruction)
        
        if result['success']:
            logger.info(f"\n✅ SUCCESS")
            logger.info(f"Quality: {result['quality_score']:.0%}")
            logger.info(f"Model: {result['model_used']}")
            logger.info(f"Time: {result['execution_time']:.2f}s")
        else:
            logger.info(f"\n❌ FAILED: {result.get('error')}")

if __name__ == "__main__":
    demo()
