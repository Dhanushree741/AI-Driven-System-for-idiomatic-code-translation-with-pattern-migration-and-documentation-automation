import ast

def analyze_code(source_code):

    tree = ast.parse(source_code)

    functions = []
    classes = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "parameters": [a.arg for a in node.args.args],
                "line": node.lineno
            })

        if isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno
            })

    return {
        "functions": functions,
        "classes": classes
    }