#!/usr/bin/env python
"""Test Module 3 functionality."""

from translator.module3 import parse_code, get_code_summary

# Test Python code parsing
python_code = '''
def hello():
    print("world")

class MyClass:
    def method(self):
        pass
'''

result = parse_code(python_code, "python")
print("=== Python Parsing Test ===")
print(f"Language: {result.get('language')}")
print(f"Functions: {len(result.get('functions', []))}")
print(f"Classes: {len(result.get('classes', []))}")
print(f"Imports: {len(result.get('imports', []))}")
print()

print("=== Summary ===")
summary = get_code_summary(python_code, "python")
print(summary)
print()

# Test JavaScript code parsing
js_code = '''
import React from 'react';
import { useState } from 'usehooks';

function App() {
  const [count, setCount] = useState(0);
  return <div>{count}</div>;
}

class MyComponent extends React.Component {
  render() {
    return <div>Hello</div>;
  }
}
'''

result = parse_code(js_code, "javascript")
print("=== JavaScript Parsing Test ===")
print(f"Language: {result.get('language')}")
print(f"Functions: {len(result.get('functions', []))}")
print(f"Classes: {len(result.get('classes', []))}")
print(f"Imports: {len(result.get('imports', []))}")
print()

print("=== Module 3 Test Complete ===")

