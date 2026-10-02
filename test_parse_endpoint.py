import sys
sys.path.insert(0, '.')

from app import app
import json

with app.test_client() as client:
    code = '''
def hello():
    print("world")

class MyClass:
    def method(self):
        pass
'''
    response = client.post('/parse', json={
        'source_code': code,
        'language': 'Python'
    })
    print('Status:', response.status_code)
    data = response.get_json()
    print('Result:', json.dumps(data, indent=2))

