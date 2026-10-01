# translator/parser.py
# Comprehensive code parser module for multi-language code analysis
# Module 3: Parses code and detects design patterns with alternatives and explanations

import ast
import re
import json
from typing import Dict, List, Any, Optional

# Import pattern detection and mapping from module3
from .module3.pattern_detector import PatternDetector, detect_pattern
from .module3.pattern_mapper import map_pattern


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
        """
        Parse code from any supported language.
        
        Args:
            code: Source code to parse
            language: Programming language
            
        Returns:
            Dictionary containing parsed structural information
        """
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
        """Parse Python code using AST."""
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
        decorators = []
        
        for node in ast.walk(tree):
            # Extract imports
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
            
            # Extract classes
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
            
            # Extract functions
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
                    "returns": node.returns.id if hasattr(node.returns, 'id') else str(node.returns) if node.returns else None
                })
            
            # Extract top-level assignments
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
        """Parse JavaScript code using regex patterns."""
        imports = []
        classes = []
        functions = []
        variables = []
        
        # Extract imports (ES6)
        import_pattern = r'import\s+(?:{[^}]+}|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, code):
            imports.append({"type": "import", "module": match.group(1)})
        
        # Extract require statements
        require_pattern = r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        for match in re.finditer(require_pattern, code):
            imports.append({"type": "require", "module": match.group(1)})
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "extends": match.group(2)
            })
        
        # Extract functions (function declarations and arrow functions)
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            functions.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
            })
        
        # Extract variable declarations
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
        """Parse TypeScript code (similar to JavaScript with type annotations)."""
        result = self.parse_javascript(code)
        result["language"] = "TypeScript"
        
        # Extract interfaces
        interface_pattern = r'interface\s+(\w+)\s*\{([^}]*)\}'
        for match in re.finditer(interface_pattern, code):
            result.setdefault("interfaces", []).append({
                "name": match.group(1),
                "properties": match.group(2)
            })
        
        # Extract type definitions
        type_pattern = r'type\s+(\w+)\s*='
        for match in re.finditer(type_pattern, code):
            result.setdefault("types", []).append({
                "name": match.group(1)
            })
        
        return result
    
    def parse_java(self, code: str) -> Dict[str, Any]:
        """Parse Java code using regex patterns."""
        imports = []
        classes = []
        methods = []
        variables = []
        
        # Extract package
        package_match = re.search(r'package\s+([\w.]+);', code)
        package = package_match.group(1) if package_match else None
        
        # Extract imports
        import_pattern = r'import\s+([\w.]+);'
        for match in re.finditer(import_pattern, code):
            imports.append({"type": "import", "package": match.group(1)})
        
        # Extract classes
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "extends": match.group(2),
                "implements": match.group(3)
            })
        
        # Extract methods
        method_pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, code):
            methods.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip() and p.strip() != '']
            })
        
        # Extract fields/variables
        field_pattern = r'(?:private|public|protected)\s+[\w<>\[\]]+\s+(\w+);'
        for match in re.finditer(field_pattern, code):
            variables.append({"name": match.group(1)})
        
        return {
            "language": "Java",
            "package": package,
            "imports": imports,
            "classes": classes,
            "methods": methods,
            "variables": variables,
            "structure": {
                "import_count": len(imports),
                "class_count": len(classes),
                "method_count": len(methods),
                "variable_count": len(variables)
            }
        }
    
    def parse_cpp(self, code: str) -> Dict[str, Any]:
        """Parse C++ code."""
        imports = []
        classes = []
        functions = []
        includes = []
        
        # Extract includes
        include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, code):
            includes.append(match.group(1))
        
        # Extract using statements
        using_pattern = r'using\s+([\w:]+);'
        for match in re.finditer(using_pattern, code):
            imports.append({"type": "using", "namespace": match.group(1)})
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+:\s+([^{]+))?\s*\{'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "inheritance": match.group(2)
            })
        
        # Extract functions
        func_pattern = r'(?:void|int|double|float|bool|string|auto)\s+(\w+)\s*\(([^)]*)\)\s*\{?'
        for match in re.finditer(func_pattern, code):
            if match.group(1) not in ['if', 'for', 'while', 'switch']:
                functions.append({
                    "name": match.group(1),
                    "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
                })
        
        return {
            "language": "C++",
            "includes": includes,
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "structure": {
                "include_count": len(includes),
                "class_count": len(classes),
                "function_count": len(functions)
            }
        }
    
    def parse_csharp(self, code: str) -> Dict[str, Any]:
        """Parse C# code."""
        imports = []
        classes = []
        methods = []
        namespaces = []
        
        # Extract namespace
        ns_pattern = r'namespace\s+([\w.]+)'
        for match in re.finditer(ns_pattern, code):
            namespaces.append(match.group(1))
        
        # Extract using statements
        using_pattern = r'using\s+([\w.]+);'
        for match in re.finditer(using_pattern, code):
            imports.append(match.group(1))
        
        # Extract classes
        class_pattern = r'(?:public|private|internal)\s+(?:abstract|sealed)?\s*class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            classes.append({"name": match.group(1)})
        
        # Extract methods
        method_pattern = r'(?:public|private|protected)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, code):
            methods.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
            })
        
        return {
            "language": "C#",
            "namespaces": namespaces,
            "imports": imports,
            "classes": classes,
            "methods": methods,
            "structure": {
                "namespace_count": len(namespaces),
                "class_count": len(classes),
                "method_count": len(methods)
            }
        }
    
    def parse_go(self, code: str) -> Dict[str, Any]:
        """Parse Go code."""
        imports = []
        functions = []
        structs = []
        
        # Extract package
        package_match = re.search(r'package\s+(\w+)', code)
        package = package_match.group(1) if package_match else None
        
        # Extract imports
        import_pattern = r'import\s+(?:\(([^)]+)\)|"([^"]+)")'
        for match in re.finditer(import_pattern, code):
            if match.group(1):
                for imp in match.group(1).split('\n'):
                    imp = imp.strip().strip('"')
                    if imp:
                        imports.append(imp)
            elif match.group(2):
                imports.append(match.group(2))
        
        # Extract structs
        struct_pattern = r'type\s+(\w+)\s+struct\s*\{'
        for match in re.finditer(struct_pattern, code):
            structs.append({"name": match.group(1)})
        
        # Extract functions
        func_pattern = r'func\s+(?:\((\w+)\s+\*?)(\w+)\s+)?(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            functions.append({
                "receiver": match.group(2),
                "name": match.group(3),
                "params": [p.strip() for p in match.group(4).split(',') if p.strip()]
            })
        
        return {
            "language": "Go",
            "package": package,
            "imports": imports,
            "structs": structs,
            "functions": functions,
            "structure": {
                "import_count": len(imports),
                "struct_count": len(structs),
                "function_count": len(functions)
            }
        }
    
    def parse_rust(self, code: str) -> Dict[str, Any]:
        """Parse Rust code."""
        imports = []
        structs = []
        impls = []
        functions = []
        
        # Extract use statements
        use_pattern = r'use\s+([\w:]+);'
        for match in re.finditer(use_pattern, code):
            imports.append(match.group(1))
        
        # Extract structs
        struct_pattern = r'struct\s+(\w+)(?:\s*\{|\s*\([^)]*\))?'
        for match in re.finditer(struct_pattern, code):
            structs.append({"name": match.group(1)})
        
        # Extract impl blocks
        impl_pattern = r'impl(?:\s+<[^>]+>)?\s+(?:\((\w+)\))?\s*\{?'
        for match in re.finditer(impl_pattern, code):
            impls.append({"target": match.group(1)})
        
        # Extract functions
        func_pattern = r'fn\s+(\w+)\s*<[^>]*>?\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            functions.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
            })
        
        return {
            "language": "Rust",
            "imports": imports,
            "structs": structs,
            "impls": impls,
            "functions": functions,
            "structure": {
                "import_count": len(imports),
                "struct_count": len(structs),
                "function_count": len(functions)
            }
        }
    
    def parse_php(self, code: str) -> Dict[str, Any]:
        """Parse PHP code."""
        imports = []
        classes = []
        functions = []
        
        # Extract use statements
        use_pattern = r'use\s+([\w\\]+);'
        for match in re.finditer(use_pattern, code):
            imports.append(match.group(1))
        
        # Extract classes
        class_pattern = r'(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "extends": match.group(2),
                "implements": match.group(3)
            })
        
        # Extract functions
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            functions.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
            })
        
        return {
            "language": "PHP",
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "structure": {
                "import_count": len(imports),
                "class_count": len(classes),
                "function_count": len(functions)
            }
        }
    
    def parse_ruby(self, code: str) -> Dict[str, Any]:
        """Parse Ruby code."""
        requires = []
        classes = []
        methods = []
        
        # Extract require statements
        require_pattern = r'require(?:_relative)?\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(require_pattern, code):
            requires.append(match.group(1))
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s*<\s*(\w+))?'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "inherits": match.group(2)
            })
        
        # Extract methods
        method_pattern = r'def\s+(\w+)'
        for match in re.finditer(method_pattern, code):
            methods.append({"name": match.group(1)})
        
        return {
            "language": "Ruby",
            "requires": requires,
            "classes": classes,
            "methods": methods,
            "structure": {
                "require_count": len(requires),
                "class_count": len(classes),
                "method_count": len(methods)
            }
        }
    
    def parse_swift(self, code: str) -> Dict[str, Any]:
        """Parse Swift code."""
        imports = []
        classes = []
        functions = []
        
        # Extract imports
        import_pattern = r'import\s+(?:struct|class|enum|protocol\s+)?(\w+)'
        for match in re.finditer(import_pattern, code):
            imports.append(match.group(1))
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s*:\s*([^{]+))?'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "inherits": match.group(2)
            })
        
        # Extract functions
        func_pattern = r'func\s+(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            functions.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
            })
        
        return {
            "language": "Swift",
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "structure": {
                "import_count": len(imports),
                "class_count": len(classes),
                "function_count": len(functions)
            }
        }
    
    def parse_kotlin(self, code: str) -> Dict[str, Any]:
        """Parse Kotlin code."""
        imports = []
        classes = []
        functions = []
        
        # Extract package
        package_match = re.search(r'package\s+([\w.]+)', code)
        package = package_match.group(1) if package_match else None
        
        # Extract imports
        import_pattern = r'import\s+([\w.]+)'
        for match in re.finditer(import_pattern, code):
            imports.append(match.group(1))
        
        # Extract classes
        class_pattern = r'(?:data\s+)?class\s+(\w+)\s*(?:\(([^)]*)\))?'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "params": match.group(2)
            })
        
        # Extract functions
        func_pattern = r'fun\s+(?:\w+\.)?(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            if match.group(1) not in ['if', 'when', 'for', 'while']:
                functions.append({
                    "name": match.group(1),
                    "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
                })
        
        return {
            "language": "Kotlin",
            "package": package,
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "structure": {
                "import_count": len(imports),
                "class_count": len(classes),
                "function_count": len(functions)
            }
        }


# Singleton instance for easy importing
parser = CodeParser()

# Initialize pattern detector for enhanced parsing
_pattern_detector = PatternDetector()


def parse_code(code: str, language: str, target_language: str = None) -> Dict[str, Any]:
    """
    Parse code with pattern detection, alternatives, code examples, and explanation.
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
            mapping = map_pattern(pattern_name, src_lang, target_language.lower())
            result["alternative"] = mapping.get("alternatives", [])
            result["code"] = [mapping.get("implementation", "")] if mapping.get("implementation") else []
            result["explanation"] = f"The detected {pattern_name} pattern can be implemented in {target_language} using: {mapping.get('description', '')}"
            
            if mapping.get("best_practices"):
                result["explanation"] += f"\n\nBest practices:\n" + "\n".join(f"- {bp}" for bp in mapping["best_practices"])
        else:
            # Get default alternatives for the pattern
            mapping = map_pattern(pattern_name, src_lang, src_lang)
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


def get_code_summary(code: str, language: str) -> str:
    """Get a human-readable summary of the parsed code."""
    result = parser.parse(code, language)
    
    if "error" in result:
        return f"Error parsing code: {result['error']}"
    
    summary = f"Language: {result['language']}\n"
    
    if "structure" in result:
        struct = result["structure"]
        summary += f"Structure:\n"
        for key, value in struct.items():
            name = key.replace("_count", "").title()
            summary += f"  - {name}: {value}\n"
    
    return summary

