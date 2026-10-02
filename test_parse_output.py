import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')

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
    data = response.get_json()
    result = data['parsed_result']
    
    print('=== PARSE RESULT ===')
    print('Language:', result.get('language'))
    print('Structure:', result.get('structure'))
    print('Alternative:', result.get('alternative'))
    print('Explanation:', result.get('explanation'))
    print('Code:', result.get('code'))
    print('Pattern:', result.get('pattern'))

