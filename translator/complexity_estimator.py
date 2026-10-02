import ast

def estimate_complexity(source_code):

    tree = ast.parse(source_code)

    loop_count = 0

    for node in ast.walk(tree):

        if isinstance(node, (ast.For, ast.While)):
            loop_count += 1

    if loop_count == 0:
        complexity = "O(1)"
    elif loop_count == 1:
        complexity = "O(n)"
    elif loop_count == 2:
        complexity = "O(n^2)"
    else:
        complexity = "O(n^k)"

    return complexity