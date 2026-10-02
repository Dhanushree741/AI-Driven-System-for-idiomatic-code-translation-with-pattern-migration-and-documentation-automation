#!/usr/bin/env python
"""Test the parser."""
from translator.parser import parse_code

code = "x = 1"
result = parse_code(code, "Python")

print("Keys:", list(result.keys()))
print("Alternative:", result.get("alternative"))
print("Code:", result.get("code"))
print("Explanation:", result.get("explanation"))

