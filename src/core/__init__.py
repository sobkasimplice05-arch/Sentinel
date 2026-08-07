"""
🛡️ CORE Module
Module central de SENTINEL
"""

from .instruction_parser import InstructionParser, Intent, Language, Domain, Complexity
from .input_pipeline import InputPipeline

__all__ = [
    "InstructionParser",
    "InputPipeline",
    "Intent",
    "Language",
    "Domain",
    "Complexity",
]

__version__ = "1.0.0"
