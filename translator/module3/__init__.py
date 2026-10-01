# Module 3: Cross-Language Pattern Migration
# Detects design patterns in source code and maps them to target language idioms

from .parser import CodeParser, parse_code, get_code_summary, parse_code_with_patterns, parse_with_analysis
from .pattern_detector import detect_pattern, PatternDetector
from .pattern_mapper import map_pattern

__all__ = [
    'CodeParser', 
    'parse_code', 
    'get_code_summary',
    'parse_code_with_patterns',
    'parse_with_analysis',
    'detect_pattern',
    'PatternDetector',
    'map_pattern'
]

