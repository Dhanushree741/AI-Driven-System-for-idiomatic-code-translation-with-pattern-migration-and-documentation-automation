import requests
import json

url = "http://127.0.0.1:5000/translate"
data = {
    "source_code": "print('hello world')",
    "source_language": "Python",
    "target_language": "JavaScript"
}

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Translated code:\n{result.get('translated_code', 'NOT FOUND')}")
except Exception as e:
    print(f"Error: {e}")

