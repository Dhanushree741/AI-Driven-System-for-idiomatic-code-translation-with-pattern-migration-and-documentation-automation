import ast
from .ast_parser import parse_python, parse_java


def detect_pattern(source_code, language):

    if language.lower() == "python":
        tree = parse_python(source_code)
        if tree is None:
            return {"pattern": "Unknown", "confidence": 0.0}

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                if node.name in ["get_instance", "__new__"]:
                    return {
                        "pattern": "Singleton",
                        "confidence": 0.9,
                        "language": "Python"
                    }

        return {"pattern": "Unknown", "confidence": 0.2}

    elif language.lower() == "java":

        struct = parse_java(source_code)

        raw = struct["raw"]

        if "private static" in raw and "getInstance" in raw:
            return {
                "pattern": "Singleton",
                "confidence": 0.95,
                "language": "Java"
            }

        if "create" in raw and "interface" in raw:
            return {
                "pattern": "Factory",
                "confidence": 0.8,
                "language": "Java"
            }

        if "notify" in raw and "Observer" in raw:
            return {
                "pattern": "Observer",
                "confidence": 0.85,
                "language": "Java"
            }

        if "Adapter" in raw:
            return {
                "pattern": "Adapter",
                "confidence": 0.8,
                "language": "Java"
            }

        return {"pattern": "Unknown", "confidence": 0.2}

    return {"pattern": "Unknown", "confidence": 0.0}