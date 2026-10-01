import requests
import json

# Test the translate endpoint
response = requests.post('http://127.0.0.1:5000/translate', 
    json={
        'source_code': 'def add(a,b): return a+b', 
        'source_language': 'Python', 
        'target_language': 'JavaScript'
    }
)

print('Status:', response.status_code)
data = response.json()
print('Success:', data.get('success'))
print('Translated:', data.get('translated_code', '')[:100])
print('Explanation:', repr(data.get('explanation', '')[:100]))
print('Alternatives:', repr(data.get('alternatives', '')[:100]))
print('Keys:', list(data.keys()))

