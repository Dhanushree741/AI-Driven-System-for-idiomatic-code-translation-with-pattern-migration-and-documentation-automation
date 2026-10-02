# Make this folder a Python package

from .model_loader import HFModelClient  # Module 1
from .prompt_builder import build_translation_prompt  # Module 2
from . import module3  # Module 3: Parser
from . import module4  # Module 4: Documentation

# Module 3: Parser Module
# Multi-language code parsing - import from module3 package
from .module3.parser import CodeParser, parse_code, get_code_summary

# Module 4: Documentation Service
from .doc_service import DocumentationService
from .semantic_analyzer import analyze_code
from .complexity_estimator import estimate_complexity
from .doc_prompt_generator import build_prompt

__all__ = [
    'HFModelClient',
    'build_translation_prompt',
    'CodeParser',
    'parse_code',
    'get_code_summary',
    'module3',
    'module4',
    # Module 4 exports
    'DocumentationService',
    'analyze_code',
    'estimate_complexity',
    'build_prompt'
]
