# Complete parse_code function with alternative, code, and explanation

from translator.module3.pattern_detector import PatternDetector
from translator.module3.pattern_mapper import PatternMapper

# Initialize pattern detector and mapper
_pattern_detector = PatternDetector()
_pattern_mapper = PatternMapper()

# Import the basic parser
from translator.parser import CodeParser
parser = CodeParser()


def parse_code(code: str, language: str, target_language: str = None) -> dict:
    """
    Parse code with pattern detection, alternatives, code examples, and explanation.
    
    Returns:
        Dictionary with:
        - language: Programming language
        - imports: List of import statements
        - class: List of classes found
        - function: List of functions found
        - import: Count of imports
        - structure: Structure counts
        - pattern: Detected pattern info
        - alternative: Alternative implementations
        - code: Code examples
        - explanation: Explanation of the code
    """
    # Get the basic parse result
    parse_result = parser.parse(code, language)
    
    # Detect design patterns in the code
    pattern_result = _pattern_detector.detect(code, language)
    
    # Build the enhanced result with new format
    result = {
        "language": language,
        "imports": parse_result.get("imports", []),
        "class": parse_result.get("classes", []),
        "function": parse_result.get("functions", []),
        "import": len(parse_result.get("imports", [])),
        "structure": parse_result.get("structure", {}),
        
        # Pattern detection results
        "pattern": {
            "detected": pattern_result.get("primary_pattern"),
            "confidence": pattern_result.get("confidence", 0.0),
            "all_patterns": pattern_result.get("patterns", [])
        },
        
        # Alternative implementations
        "alternative": [],
        
        # Code examples
        "code": [],
        
        # Explanation
        "explanation": ""
    }
    
    # If a pattern is detected, get alternatives and code examples
    if pattern_result.get("primary_pattern"):
        pattern_name = pattern_result["primary_pattern"]
        src_lang = language.lower()
        
        if target_language:
            # Map to target language
            mapping = _pattern_mapper.map_pattern(pattern_name, src_lang, target_language.lower())
            result["alternative"] = mapping.get("alternatives", [])
            result["code"] = [mapping.get("implementation", "")] if mapping.get("implementation") else []
            result["explanation"] = f"The detected {pattern_name} pattern can be implemented in {target_language} using: {mapping.get('description', '')}"
            
            if mapping.get("best_practices"):
                result["explanation"] += f"\n\nBest practices:\n" + "\n".join(f"- {bp}" for bp in mapping["best_practices"])
        else:
            # Get default alternatives for the pattern
            mapping = _pattern_mapper.map_pattern(pattern_name, src_lang, src_lang)
            result["alternative"] = mapping.get("alternatives", [])
            result["code"] = [mapping.get("implementation", "")] if mapping.get("implementation") else []
            result["explanation"] = f"Detected {pattern_name} pattern in {language} code. {mapping.get('description', '')}"
            
            if mapping.get("best_practices"):
                result["explanation"] += f"\n\nBest practices:\n" + "\n".join(f"- {bp}" for bp in mapping["best_practices"])
    
    # If no pattern detected, provide generic explanation
    if not result["pattern"]["detected"]:
        result["explanation"] = f"Parsed {language} code: {result['structure'].get('function_count', 0)} functions, {result['structure'].get('class_count', 0)} classes found. No specific design pattern detected."
        result["alternative"] = ["direct_translation", "functional_approach", "class_based_approach"]
        result["code"] = [code]
    
    return result


# Example usage:
if __name__ == "__main__":
    # Test with simple code
    code = "x = 1"
    result = parse_code(code, "Python")
    print("Keys:", list(result.keys()))
    print("Alternative:", result["alternative"])
    print("Code:", result["code"])
    print("Explanation:", result["explanation"])
    
    print("\n" + "="*50 + "\n")
    
    # Test with Singleton pattern
    singleton_code = '''
class Singleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
'''
    result2 = parse_code(singleton_code, "Python", "Java")
    print("Pattern:", result2["pattern"]["detected"])
    print("Alternative:", result2["alternative"])
    print("Explanation:", result2["explanation"][:200])

