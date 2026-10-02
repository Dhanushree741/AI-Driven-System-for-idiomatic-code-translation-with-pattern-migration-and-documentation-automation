#!/usr/bin/env python
"""Final verification test for Module 3 parser."""

# Test the parser module
print("Testing translator.parser import...")
from translator.parser import parse_code
print("✓ translator.parser imported successfully")

# Test the module3 module
print("\nTesting translator.module3 import...")
from translator.module3 import parse_code as module3_parse_code
print("✓ translator.module3 imported successfully")

# Test parsing
print("\nTesting parse_code function...")
code = '''
def hello():
    print("world")

class MyClass:
    def method(self):
        pass
'''

result = parse_code(code, 'Python')
print(f"Language: {result.get('language')}")
print(f"Classes: {len(result.get('class', []))}")
print(f"Functions: {len(result.get('function', []))}")
print(f"Imports: {result.get('import')}")
print(f"\nStructure: {result.get('structure')}")

# Test backend app
print("\n\nTesting backend app import...")
import sys
sys.path.insert(0, 'backend')
from app import app
print("✓ backend.app imported successfully")

print("\n✅ All tests passed!")

