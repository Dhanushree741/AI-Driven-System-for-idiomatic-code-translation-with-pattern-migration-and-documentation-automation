from translator.module3 import parse_code

code = '''
def hello():
    print("world")

class MyClass:
    def method(self):
        pass
'''

result = parse_code(code, 'Python')
print("=== PARSE RESULT ===")
print(result)

