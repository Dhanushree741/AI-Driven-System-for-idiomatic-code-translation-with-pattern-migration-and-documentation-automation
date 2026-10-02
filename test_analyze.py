import requests

# Test the /analyze endpoint
url = "http://127.0.0.1:5000/analyze"
data = {
    "source_code": "def add(a, b):\n    return a + b",
    "source_language": "Python",
    "target_language": "JavaScript"
}

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Explanation:\n{result.get('explanation', 'NOT FOUND')}")
    print(f"\nAlternatives:\n{result.get('alternatives', 'NOT FOUND')}")
except Exception as e:
    print(f"Error: {e}")

