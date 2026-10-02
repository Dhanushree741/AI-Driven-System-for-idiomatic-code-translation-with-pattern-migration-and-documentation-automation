import ast


def parse_python(code: str):
    """
    Parse Python code into AST
    """
    try:
        tree = ast.parse(code)
        return tree
    except Exception:
        return None


def parse_java(code: str):
    """
    Basic Java structure extraction
    (lightweight parser)
    """

    structure = {
        "classes": [],
        "methods": [],
        "raw": code
    }

    lines = code.split("\n")

    for line in lines:

        line = line.strip()

        if "class " in line:
            structure["classes"].append(line)

        if "(" in line and ")" in line and "{" in line:
            structure["methods"].append(line)

    return structure