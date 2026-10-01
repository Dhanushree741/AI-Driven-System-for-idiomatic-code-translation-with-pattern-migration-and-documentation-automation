# translator/module3/parser.py
# Comprehensive code parser module for multi-language code analysis
# Module 3: Parses code and detects design patterns with alternatives and explanations

import ast
import re
import json
from typing import Dict, List, Any, Optional

# Import pattern detection and mapping
from .pattern_detector import PatternDetector, detect_pattern
from .pattern_mapper import map_pattern


class CodeParser:
    """Multi-language code parser for extracting structural information."""
    
    def __init__(self):
        self.supported_languages = {
            'python': self.parse_python,
            'javascript': self.parse_javascript,
            'typescript': self.parse_typescript,
            'java': self.parse_java,
            'cpp': self.parse_cpp,
            'csharp': self.parse_csharp,
            'go': self.parse_go,
            'rust': self.parse_rust,
            'php': self.parse_php,
            'ruby': self.parse_ruby,
            'swift': self.parse_swift,
            'kotlin': self.parse_kotlin,
        }
    
    def parse(self, code: str, language: str) -> Dict[str, Any]:
        lang = language.lower()
        
        if lang not in self.supported_languages:
            return {
                "language": language,
                "error": f"Unsupported language: {language}",
                "raw": code
            }
        
        try:
            return self.supported_languages[lang](code)
        except Exception as e:
            return {
                "language": language,
                "error": str(e),
                "raw": code
            }
    
    def parse_python(self, code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "language": "Python",
                "error": f"Syntax error: {str(e)}",
                "raw": code
            }
        
        imports = []
        classes = []
        functions = []
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "name": alias.name,
                        "alias": alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                imports.append({
                    "type": "from",
                    "module": node.module,
                    "names": [alias.name for alias in node.names],
                    "level": node.level
                })
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "bases": [base.id if hasattr(base, 'id') else str(base) for base in node.bases],
                    "methods": [],
                    "decorators": [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
                }
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info["methods"].append({
                            "name": item.name,
                            "args": [arg.arg for arg in item.args.args],
                            "decorators": [d.id if hasattr(d, 'id') else str(d) for d in item.decorator_list]
                        })
                classes.append(class_info)
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
                    "returns": node.returns.id if hasattr(node.returns, 'id') else str(node.returns) if node.returns else None
                })
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            "name": target.id,
                            "type": "assignment"
                        })
        
        return {
            "language": "Python",
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "variables": variables,
            "structure": {
                "import_count": len(imports),
                "class_count": len(classes),
                "function_count": len(functions),
                "variable_count": len(variables)
            }
        }
    
    def parse_javascript(self, code: str) -> Dict[str, Any]:
        imports = []
        classes = []
        functions = []
        variables = []
        
        import_pattern = r'import\s+(?:{[^}]+}|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, code):
            imports.append({"type": "import", "module": match.group(1)})
        
        require_pattern = r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        for match in re.finditer(require_pattern, code):
            imports.append({"type": "require", "module": match.group(1)})
        
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "extends": match.group(2)
            })
        
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            functions.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
            })
        
        var_pattern = r'(?:const|let|var)\s+(\w+)\s*='
        for match in re.finditer(var_pattern, code):
            variables.append({"name": match.group(1)})
        
        return {
            "language": "JavaScript",
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "variables": variables,
            "structure": {
                "import_count": len(imports),
                "class_count": len(classes),
                "function_count": len(functions),
                "variable_count": len(variables)
            }
        }
    
    def parse_typescript(self, code: str) -> Dict[str, Any]:
        result = self.parse_javascript(code)
        result["language"] = "TypeScript"
        return result
    
    def parse_java(self, code: str) -> Dict[str, Any]:
        imports = []
        classes = []
        methods = []
        variables = []
        
        import_pattern = r'import\s+([\w.]+);'
        for match in re.finditer(import_pattern, code):
            imports.append({"type": "import", "package": match.group(1)})
        
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, code):
            classes.append({"name": match.group(1), "extends": match.group(2)})
        
        method_pattern = r'(?:public|private|protected|static)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, code):
            methods.append({"name": match.group(1), "params": [p.strip() for p in match.group(2).split(',') if p.strip()]})
        
        return {"language": "Java", "imports": imports, "classes": classes, "methods": methods, "structure": {"import_count": len(imports), "class_count": len(classes), "method_count": len(methods)}}
    
    def parse_cpp(self, code: str) -> Dict[str, Any]:
        includes = []
        include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, code):
            includes.append(match.group(1))
        return {"language": "C++", "includes": includes, "structure": {"include_count": len(includes)}}
    
    def parse_csharp(self, code: str) -> Dict[str, Any]:
        return {"language": "C#", "structure": {}}
    
    def parse_go(self, code: str) -> Dict[str, Any]:
        return {"language": "Go", "structure": {}}
    
    def parse_rust(self, code: str) -> Dict[str, Any]:
        return {"language": "Rust", "structure": {}}
    
    def parse_php(self, code: str) -> Dict[str, Any]:
        return {"language": "PHP", "structure": {}}
    
    def parse_ruby(self, code: str) -> Dict[str, Any]:
        return {"language": "Ruby", "structure": {}}
    
    def parse_swift(self, code: str) -> Dict[str, Any]:
        return {"language": "Swift", "structure": {}}
    
    def parse_kotlin(self, code: str) -> Dict[str, Any]:
        return {"language": "Kotlin", "structure": {}}


parser = CodeParser()
_pattern_detector = PatternDetector()


def parse_code(code: str, language: str, target_language: str = None) -> Dict[str, Any]:
    parse_result = parser.parse(code, language)
    pattern_result = _pattern_detector.detect(code, language)
    
    result = {
        "language": language,
        "imports": parse_result.get("imports", []),
        "class": parse_result.get("classes", []),
        "function": parse_result.get("functions", []),
        "import": len(parse_result.get("imports", [])),
        "structure": parse_result.get("structure", {}),
        "pattern": {
            "detected": pattern_result.get("primary_pattern"),
            "confidence": pattern_result.get("confidence", 0.0),
            "all_patterns": pattern_result.get("patterns", [])
        },
        "alternative": [],
        "code": [],
        "explanation": ""
    }
    
    if pattern_result.get("primary_pattern"):
        pattern_name = pattern_result["primary_pattern"]
        src_lang = language.lower()
        
        if target_language:
            mapping = map_pattern(pattern_name, src_lang, target_language.lower())
        else:
            mapping = map_pattern(pattern_name, src_lang, src_lang)
        
        alternatives = mapping.get("alternatives", [])
        if alternatives and isinstance(alternatives[0], dict):
            result["alternative"] = alternatives
        else:
            result["alternative"] = [{"name": alt, "code": ""} for alt in alternatives]
        
        result["code"] = [mapping.get("implementation", "")] if mapping.get("implementation") else []
        
        result["explanation"] = _build_comprehensive_explanation(
            pattern_name, 
            language, 
            target_language, 
            mapping
        )
    
    if not result["pattern"]["detected"]:
        result["explanation"] = _build_generic_explanation(code, language, parse_result)
        result["alternative"] = [
            {"name": "direct_translation", "code": _get_direct_translation_code(code, language)},
            {"name": "functional_approach", "code": _get_functional_approach_code(code, language)},
            {"name": "class_based_approach", "code": _get_class_based_approach_code(code, language)}
        ]
        result["code"] = [code]
    
    return result


def get_code_summary(code: str, language: str) -> str:
    result = parser.parse(code, language)
    if "error" in result:
        return f"Error parsing code: {result['error']}"
    summary = f"Language: {result['language']}\n"
    if "structure" in result:
        struct = result["structure"]
        for key, value in struct.items():
            name = key.replace("_count", "").title()
            summary += f"  - {name}: {value}\n"
    return summary


def _build_comprehensive_explanation(pattern_name: str, source_lang: str, target_lang: str, mapping: Dict) -> str:
    """Build explanation as a plain paragraph without markdown."""
    explanation = []
    
    explanation.append(f"This {source_lang.title()} code uses the {pattern_name} design pattern. ")
    
    description = mapping.get("description", "")
    if description:
        explanation.append(f"The {pattern_name} pattern {description.lower()} ")
    
    explanation.append(f"When translating to {target_lang.title() if target_lang else source_lang}, ")
    
    strategy = mapping.get("strategy", "direct_translation")
    explanation.append(f"the recommended approach is {strategy.replace('_', ' ')}. ")
    
    best_practices = mapping.get("best_practices", [])
    if best_practices:
        explanation.append(f"Key best practices include: {best_practices[0]}")
        if len(best_practices) > 1:
            explanation.append(f" and {best_practices[1]}")
        explanation.append(".")
    
    return "".join(explanation)


def _build_generic_explanation(code: str, language: str, parse_result: Dict) -> str:
    """Build a plain paragraph explanation without markdown formatting."""
    structure = parse_result.get("structure", {})
    func_count = structure.get('function_count', 0)
    class_count = structure.get('class_count', 0)
    import_count = structure.get('import_count', 0)
    
    # Get function names
    functions = parse_result.get("functions", [])
    func_names = [f.get("name", "unknown") for f in functions]
    
    # Build paragraph explanation
    explanation = []
    
    explanation.append(f"This {language.title()} code defines ")
    if func_count == 0 and class_count == 0:
        explanation.append("a simple code snippet with basic statements.")
    elif class_count > 0:
        class_names = [c.get("name", "unknown") for c in parse_result.get("classes", [])]
        explanation.append(f"a class named '{class_names[0]}' ")
        if func_count > 0:
            explanation.append(f"with {func_count} method(s) including: {', '.join(func_names[:3])}")
            if func_count > 3:
                explanation.append(f" and {func_count - 3} more")
            explanation.append(".")
    else:
        explanation.append(f"{func_count} function(s) ")
        if func_count > 0:
            explanation.append(f"named: {', '.join(func_names[:3])}")
            if func_count > 3:
                explanation.append(f" and {func_count - 3} more")
            explanation.append(".")
    
    if import_count > 0:
        explanation.append(f" The code imports {import_count} module(s).")
    
    explanation.append(" This is a straightforward implementation without any specific design pattern.")
    
    return "".join(explanation)


def _get_pattern_benefits(pattern_name: str) -> str:
    benefits = {
        "Singleton": "ensures that a class has only one instance while providing a global access point",
        "Factory": "provides an interface for creating objects but lets subclasses decide which class to instantiate",
        "Observer": "defines a one-to-many dependency between objects so when one object changes state, all dependents are notified",
        "Adapter": "converts the interface of a class into another interface clients expect",
        "Strategy": "defines a family of algorithms, encapsulates each one, and makes them interchangeable",
        "Decorator": "attaches additional responsibilities to an object dynamically",
        "Repository": "mediates between the domain and data mapping layers using a collection-like interface",
        "Dependency Injection": "is a technique where an object receives other objects it depends on"
    }
    return benefits.get(pattern_name, "helps improve code organization and maintainability")


def _get_direct_translation_code(code: str, language: str) -> str:
    if language.lower() == "python":
        return "# Direct translation - same code\n" + code
    elif language.lower() == "javascript":
        return "// Direct translation - same code\n" + code
    return code


def _get_functional_approach_code(code: str, language: str) -> str:
    if language.lower() == "python":
        return """# Functional Approach Example
from functools import reduce

def process_data(items):
    return reduce(lambda acc, x: acc + x, items, 0)

def transform_data(items):
    return list(map(lambda x: x * 2, filter(lambda x: x > 0, items)))
"""
    elif language.lower() == "javascript":
        return """// Functional Approach Example
const processData = (items) => items.reduce((acc, x) => acc + x, 0);
const transformData = (items) => items.filter(x => x > 0).map(x => x * 2);
"""
    return code


def _get_class_based_approach_code(code: str, language: str) -> str:
    if language.lower() == "python":
        return """# Class-based Approach Example
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return [self._transform(item) for item in self.data]
    
    def _transform(self, item):
        return item * 2

processor = DataProcessor([1, 2, 3])
result = processor.process()
"""
    elif language.lower() == "javascript":
        return """// Class-based Approach Example
class DataProcessor {
    constructor(data) { this.data = data; }
    process() { return this.data.map(item => this.transform(item)); }
    transform(item) { return item * 2; }
}
const processor = new DataProcessor([1, 2, 3]);
const result = processor.process();
"""
    return code


def parse_code_with_patterns(code: str, language: str, target_language: str = None) -> Dict[str, Any]:
    return parse_code(code, language, target_language)


def parse_with_analysis(code: str, language: str, target_language: str = None) -> Dict[str, Any]:
    return parse_code_with_patterns(code, language, target_language)

