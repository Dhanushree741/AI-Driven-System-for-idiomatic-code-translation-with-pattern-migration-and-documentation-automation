# translator/module3/pattern_detector.py
# Cross-Language Pattern Detection Module

import ast
import re
from typing import Dict, List, Any, Optional


class PatternDetector:
    """
    Detects design patterns in source code across multiple programming languages.
    Supports: Python, Java, JavaScript, TypeScript, C++, C#, Go, Rust
    """
    
    # Pattern signatures for different languages
    PATTERNS = {
        "Singleton": {
            "python": [
                (r"_instance\s*=\s*None", 0.9),
                (r"if\s+.*instance\s*is\s*None", 0.8),
                (r"@classmethod\s+def\s+get_instance", 0.9),
            ],
            "java": [
                (r"private\s+static\s+.*instance", 1.0),
                (r"public\s+static\s+.*getInstance", 1.0),
                (r"private\s+.*\s+constructor", 0.7),
            ],
            "javascript": [
                (r"instance\s*=\s*null", 0.7),
                (r"getInstance\s*\(", 0.8),
                (r"static\s+get\s+instance", 0.9),
            ],
            "typescript": [
                (r"private\s+static\s+instance", 1.0),
                (r"public\s+static\s+getInstance", 1.0),
            ],
            "cpp": [
                (r"static.*instance", 0.9),
                (r"GetInstance\s*\(", 0.8),
            ],
            "csharp": [
                (r"private\s+static\s+readonly", 1.0),
                (r"public\s+static\s+.*Instance", 1.0),
            ],
            "go": [
                (r"var\s+instance\s*=", 0.8),
                (r"GetInstance\s*\(", 0.7),
            ],
            "rust": [
                (r"lazy_static!", 0.9),
                (r"impl\s+.*Singleton", 0.8),
            ],
        },
        "Factory Method": {
            "python": [
                (r"def\s+create\s*\(", 0.8),
                (r"def\s+factory\s*\(", 0.7),
                (r"@classmethod\s+def\s+create", 0.8),
            ],
            "java": [
                (r"public\s+.*create\(", 0.9),
                (r"Factory", 0.6),
                (r"abstract\s+class.*Factory", 0.8),
            ],
            "javascript": [
                (r"create\w*\s*\(", 0.7),
                (r"factory\s*:\s*{", 0.7),
            ],
            "typescript": [
                (r"create\w*\s*\(", 0.7),
                (r"interface\s+\w*Factory", 0.8),
            ],
            "cpp": [
                (r"create\w*\s*\(", 0.7),
                (r"virtual\s+.*create", 0.8),
            ],
            "csharp": [
                (r"Create\w*\s*\(", 0.8),
                (r"interface\s+\w*Factory", 0.8),
            ],
            "go": [
                (r"func\s+New\w+", 0.8),
                (r"func\s+Create", 0.7),
            ],
            "rust": [
                (r"fn\s+new\w*\s*\(", 0.7),
                (r"impl\s+.*Factory", 0.8),
            ],
        },
        "Observer": {
            "python": [
                (r"def\s+notify\s*\(", 0.8),
                (r"def\s+update\s*\(", 0.8),
                (r"def\s+attach\s*\(", 0.8),
                (r"def\s+subscribe\s*\(", 0.7),
            ],
            "java": [
                (r"notifyObservers\s*\(", 0.9),
                (r"addObserver\s*\(", 0.9),
                (r"Observer\s+", 0.7),
                (r"EventListener", 0.7),
            ],
            "javascript": [
                (r"addEventListener\s*\(", 0.9),
                (r"on\w+\s*=", 0.7),
                (r"emit\s*\(", 0.8),
            ],
            "typescript": [
                (r"addEventListener\s*\(", 0.9),
                (r"Subject\s+from\s+rxjs", 0.9),
                (r"Observer\s+interface", 0.9),
            ],
            "cpp": [
                (r"notify\s*\(", 0.7),
                (r"Observer\s+", 0.8),
            ],
            "csharp": [
                (r"Notify\s*\(", 0.8),
                (r"IObserver\s+", 0.9),
                (r"event\s+", 0.7),
            ],
            "go": [
                (r"Notify\s*\(", 0.8),
                (r"Observer\s+interface", 0.8),
            ],
            "rust": [
                (r"notify\s*\(", 0.7),
                (r"Observer\s+trait", 0.9),
            ],
        },
        "Adapter": {
            "python": [
                (r"class\s+\w*Adapter", 0.9),
                (r"def\s+adapt\s*\(", 0.7),
                (r"wrapper", 0.5),
            ],
            "java": [
                (r"class\s+\w*Adapter", 1.0),
                (r"implements\s+.*Adapter", 0.9),
            ],
            "javascript": [
                (r"Adapter\s*=", 0.8),
                (r"wrap\s*\(", 0.6),
            ],
            "typescript": [
                (r"class\s+\w*Adapter", 0.9),
                (r"implements\s+.*Adapter", 0.9),
            ],
            "cpp": [
                (r"Adapter", 0.7),
                (r"wrapper", 0.5),
            ],
            "csharp": [
                (r"class\s+\w*Adapter", 1.0),
                (r"implements\s+.*Adapter", 0.9),
            ],
            "go": [
                (r"Adapter", 0.7),
                (r"wrapper", 0.6),
            ],
            "rust": [
                (r"Adapter", 0.7),
                (r"wrap\s*\(", 0.6),
            ],
        },
        "Strategy": {
            "python": [
                (r"def\s+set_strategy\s*\(", 0.8),
                (r"@strategy", 0.7),
                (r"Strategy\s+pattern", 0.6),
            ],
            "java": [
                (r"setStrategy\s*\(", 0.9),
                (r"Strategy\s+interface", 0.9),
            ],
            "javascript": [
                (r"setStrategy\s*\(", 0.8),
                (r"strategy\s*:\s*{", 0.7),
            ],
            "typescript": [
                (r"setStrategy\s*\(", 0.8),
                (r"interface\s+.*Strategy", 0.9),
            ],
            "cpp": [
                (r"setStrategy\s*\(", 0.8),
                (r"Strategy\s+interface", 0.8),
            ],
            "csharp": [
                (r"SetStrategy\s*\(", 0.9),
                (r"IStrategy\s+", 0.9),
            ],
            "go": [
                (r"Strategy\s+interface", 0.9),
                (r"SetStrategy\s*\(", 0.8),
            ],
            "rust": [
                (r"Strategy\s+trait", 0.9),
                (r"set_strategy\s*\(", 0.8),
            ],
        },
        "Decorator": {
            "python": [
                (r"@", 0.3),  # Decorator syntax
                (r"@property", 0.8),
                (r"@classmethod", 0.8),
                (r"@staticmethod", 0.8),
            ],
            "java": [
                (r"@Override", 0.8),
                (r"@Deprecated", 0.7),
                (r"@FunctionalInterface", 0.9),
            ],
            "javascript": [
                (r"@\w+", 0.8),  # Decorator syntax
                (r"\.extend\s*\(", 0.7),
            ],
            "typescript": [
                (r"@\w+", 0.9),  # Decorator syntax
                (r"@Component", 0.9),
                (r"@Injectable", 0.9),
            ],
            "cpp": [
                (r"decorator", 0.5),
            ],
            "csharp": [
                (r"\[.*\]", 0.7),  # Attribute
                (r"\[Attribute\]", 0.8),
            ],
            "go": [
                (r"decorator", 0.5),
            ],
            "rust": [
                (r"#\[.*\]", 0.9),  # Attribute
                (r"macro_rules!", 0.7),
            ],
        },
        "Repository": {
            "python": [
                (r"class\s+\w*Repository", 1.0),
                (r"def\s+get_all\s*\(", 0.8),
                (r"def\s+find_by_id\s*\(", 0.8),
            ],
            "java": [
                (r"interface\s+\w*Repository", 1.0),
                (r"@Repository", 0.9),
                (r"CrudRepository", 0.9),
            ],
            "javascript": [
                (r"class\s+\w*Repository", 0.9),
                (r"Repository\s*=", 0.8),
            ],
            "typescript": [
                (r"class\s+\w*Repository", 0.9),
                (r"interface\s+.*Repository", 0.9),
            ],
            "cpp": [
                (r"Repository", 0.6),
            ],
            "csharp": [
                (r"interface\s+IRepository", 1.0),
                (r"class\s+\w*Repository", 0.9),
            ],
            "go": [
                (r"Repository", 0.6),
            ],
            "rust": [
                (r"Repository", 0.6),
            ],
        },
        "Dependency Injection": {
            "python": [
                (r"def\s+__init__\s*\(.*container", 0.8),
                (r"@inject", 0.9),
                (r"injector", 0.8),
            ],
            "java": [
                (r"@Inject", 1.0),
                (r"@Autowired", 1.0),
                (r"@Component", 0.9),
            ],
            "javascript": [
                (r"inject\s*\(", 0.8),
                (r"@Injectable", 0.9),
            ],
            "typescript": [
                (r"@Injectable", 1.0),
                (r"@Inject", 1.0),
                (r"constructor\s*\([^)]*@", 0.9),
            ],
            "cpp": [
                (r"DI", 0.5),
                (r"inject", 0.6),
            ],
            "csharp": [
                (r"\[Inject\]", 1.0),
                (r"\[Autowired\]", 1.0),
                (r"interface\s+.*Service", 0.7),
            ],
            "go": [
                (r"wire\.Generate", 0.9),
                (r"fx\.Provide", 0.9),
            ],
            "rust": [
                (r"inject", 0.7),
                (r"Dependency", 0.6),
            ],
        },
    }
    
    def __init__(self):
        self.language_aliases = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c++': 'cpp',
            'c#': 'csharp',
            'cs': 'csharp',
            'go': 'go',
            'golang': 'go',
            'rust': 'rust',
            'rs': 'rust',
        }
    
    def normalize_language(self, language: str) -> str:
        """Normalize language name to standard form."""
        lang = language.lower().strip()
        return self.language_aliases.get(lang, lang)
    
    def detect(self, source_code: str, language: str) -> Dict[str, Any]:
        """
        Detect design patterns in source code.
        
        Args:
            source_code: Source code to analyze
            language: Programming language of the source code
            
        Returns:
            Dictionary containing detected patterns and confidence scores
        """
        lang = self.normalize_language(language)
        
        if lang not in ['python', 'java', 'javascript', 'typescript', 'cpp', 'csharp', 'go', 'rust']:
            return {
                "language": language,
                "patterns": [],
                "primary_pattern": None,
                "confidence": 0.0,
                "error": f"Unsupported language: {language}"
            }
        
        detected_patterns = []
        
        # Check each pattern type
        for pattern_name, pattern_signatures in self.PATTERNS.items():
            if lang not in pattern_signatures:
                continue
            
            best_confidence = 0.0
            matched_signatures = []
            
            for regex_pattern, base_confidence in pattern_signatures[lang]:
                matches = re.findall(regex_pattern, source_code, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Add to confidence based on number of matches
                    match_bonus = min(len(matches) * 0.1, 0.2)
                    confidence = min(base_confidence + match_bonus, 1.0)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        matched_signatures.append({
                            "signature": regex_pattern,
                            "matches": len(matches)
                        })
            
            if best_confidence > 0.5:  # Minimum threshold
                detected_patterns.append({
                    "name": pattern_name,
                    "confidence": round(best_confidence, 2),
                    "signatures": matched_signatures
                })
        
        # Sort by confidence
        detected_patterns.sort(key=lambda x: x["confidence"], reverse=True)
        
        primary = detected_patterns[0] if detected_patterns else None
        
        return {
            "language": language,
            "patterns": detected_patterns,
            "primary_pattern": primary["name"] if primary else None,
            "confidence": primary["confidence"] if primary else 0.0,
            "pattern_count": len(detected_patterns)
        }
    
    def get_pattern_info(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific pattern."""
        return self.PATTERNS.get(pattern_name)


def detect_pattern(source_code: str, language: str) -> Dict[str, Any]:
    """
    Convenience function to detect patterns in source code.
    
    Args:
        source_code: Source code to analyze
        language: Programming language
        
    Returns:
        Dictionary with detection results
    """
    detector = PatternDetector()
    return detector.detect(source_code, language)

