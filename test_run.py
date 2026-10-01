import requests
import json

# Test the translation endpoint
data = {
    "source_code": "def hello():\n    print('hi')",
    "source_language": "Python",
    "target_language": "JavaScript"
}

response = requests.post("http://127.0.0.1:5000/translate", json=data)
print("Status:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2))

