def build_prompt(source_code, semantic_data, complexity):

    return f"""
You are an expert software engineer.

Generate professional documentation.

Functions:
{semantic_data['functions']}

Classes:
{semantic_data['classes']}

Estimated Time Complexity: {complexity}

Create sections:

1. Overview
2. Class Description
3. Function Documentation
4. Example Usage
5. Complexity Analysis
6. Best Practices

Code:
{source_code}
"""