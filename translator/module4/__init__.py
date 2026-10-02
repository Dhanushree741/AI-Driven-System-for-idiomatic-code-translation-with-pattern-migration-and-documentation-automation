# Module 4: Documentation Service
# Provides AI-powered code documentation generation

from ..doc_service import DocumentationService
from ..semantic_analyzer import analyze_code
from ..complexity_estimator import estimate_complexity
from ..doc_prompt_generator import build_prompt

__all__ = [
    'DocumentationService',
    'analyze_code',
    'estimate_complexity',
    'build_prompt'
]

