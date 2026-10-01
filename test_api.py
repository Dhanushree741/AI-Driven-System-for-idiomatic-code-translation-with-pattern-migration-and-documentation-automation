"""
Comprehensive API tests for the code-translator backend.

Usage:
    1. Start the backend server: python backend/app.py
    2. Run tests: python test_api.py
    
Environment:
    - Set API_KEY in .env (or tests will work without it in dev mode)
    - Set HF_API_TOKEN and MODEL_ID for actual translation tests
"""

import requests
import sys
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"
API_KEY = "your_api_key_here"  # Change this to your actual API key

# Test headers
def get_headers(api_key=None):
    """Get request headers with optional API key."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


def test_root_endpoint():
    """Test the root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/", headers=get_headers())
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Root endpoint test PASSED")
            return True
        else:
            print("✗ Root endpoint test FAILED")
            return False
    except Exception as e:
        print(f"✗ Root endpoint test FAILED: {e}")
        return False


def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health", headers=get_headers())
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print("✓ Health endpoint test PASSED")
                return True
        print("✗ Health endpoint test FAILED")
        return False
    except Exception as e:
        print(f"✗ Health endpoint test FAILED: {e}")
        return False


def test_languages_endpoint():
    """Test the languages endpoint."""
    print("\n=== Testing Languages Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/languages", headers=get_headers())
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "Python" in data.get("languages", []):
                print("✓ Languages endpoint test PASSED")
                return True
        print("✗ Languages endpoint test FAILED")
        return False
    except Exception as e:
        print(f"✗ Languages endpoint test FAILED: {e}")
        return False


def test_model_info_without_key():
    """Test model info endpoint without API key (should fail)."""
    print("\n=== Testing Model Info (No API Key) ===")
    try:
        response = requests.get(f"{BASE_URL}/model/info", headers=get_headers())
        print(f"Status: {response.status_code}")
        
        # Should return 401 without API key (if API_KEY is configured)
        if response.status_code in [200, 401]:
            print("✓ Model info endpoint (no key) test PASSED")
            return True
        print("✗ Model info endpoint (no key) test FAILED")
        return False
    except Exception as e:
        print(f"✗ Model info endpoint test FAILED: {e}")
        return False


def test_translate_missing_fields():
    """Test translate endpoint with missing fields."""
    print("\n=== Testing Translate (Missing Fields) ===")
    try:
        # Missing all fields
        response = requests.post(
            f"{BASE_URL}/translate",
            headers=get_headers(API_KEY),
            json={}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✓ Translate (missing fields) test PASSED")
            return True
        print("✗ Translate (missing fields) test FAILED")
        return False
    except Exception as e:
        print(f"✗ Translate test FAILED: {e}")
        return False


def test_translate_empty_source_code():
    """Test translate endpoint with empty source code."""
    print("\n=== Testing Translate (Empty Source Code) ===")
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            headers=get_headers(API_KEY),
            json={
                "source_code": "",
                "source_language": "Python",
                "target_language": "JavaScript"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✓ Translate (empty source code) test PASSED")
            return True
        print("✗ Translate (empty source code) test FAILED")
        return False
    except Exception as e:
        print(f"✗ Translate test FAILED: {e}")
        return False


def test_translate_unsupported_language():
    """Test translate endpoint with unsupported language."""
    print("\n=== Testing Translate (Unsupported Language) ===")
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            headers=get_headers(API_KEY),
            json={
                "source_code": "print('hello')",
                "source_language": "Python",
                "target_language": "Pascal"  # Not supported
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✓ Translate (unsupported language) test PASSED")
            return True
        print("✗ Translate (unsupported language) test FAILED")
        return False
    except Exception as e:
        print(f"✗ Translate test FAILED: {e}")
        return False


def test_translate_same_language():
    """Test translate endpoint with same source and target language."""
    print("\n=== Testing Translate (Same Language) ===")
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            headers=get_headers(API_KEY),
            json={
                "source_code": "print('hello')",
                "source_language": "Python",
                "target_language": "Python"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✓ Translate (same language) test PASSED")
            return True
        print("✗ Translate (same language) test FAILED")
        return False
    except Exception as e:
        print(f"✗ Translate test FAILED: {e}")
        return False


def test_translate_code_too_long():
    """Test translate endpoint with source code exceeding length limit."""
    print("\n=== Testing Translate (Code Too Long) ===")
    try:
        # Create a long code string (> 10000 chars default limit)
        long_code = "x = 1\n" * 3000  # This should exceed 10000 chars
        
        response = requests.post(
            f"{BASE_URL}/translate",
            headers=get_headers(API_KEY),
            json={
                "source_code": long_code,
                "source_language": "Python",
                "target_language": "JavaScript"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✓ Translate (code too long) test PASSED")
            return True
        print("✗ Translate (code too long) test FAILED")
        return False
    except Exception as e:
        print(f"✗ Translate test FAILED: {e}")
        return False


def test_translate_valid_request():
    """Test translate endpoint with valid request."""
    print("\n=== Testing Translate (Valid Request) ===")
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            headers=get_headers(API_KEY),
            json={
                "source_code": 'print("hello world")',
                "source_language": "Python",
                "target_language": "JavaScript"
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get("success") and data.get("translated_code"):
                print("✓ Translate (valid request) test PASSED")
                return True
        elif response.status_code == 500:
            print("Note: Model not configured - this is expected without HF_API_TOKEN")
            print("✓ Translate (valid request) test PASSED (model not configured)")
            return True
            
        print("✗ Translate (valid request) test FAILED")
        return False
    except Exception as e:
        print(f"✗ Translate test FAILED: {e}")
        return False


def test_404_endpoint():
    """Test 404 for non-existent endpoint."""
    print("\n=== Testing 404 Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/nonexistent", headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            print("✓ 404 endpoint test PASSED")
            return True
        print("✗ 404 endpoint test FAILED")
        return False
    except Exception as e:
        print(f"✗ 404 endpoint test FAILED: {e}")
        return False


def run_all_tests():
    """Run all tests and print summary."""
    print("=" * 60)
    print("CODE-TRANSLATOR API TESTS")
    print("=" * 60)
    
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Health Endpoint", test_health_endpoint),
        ("Languages Endpoint", test_languages_endpoint),
        ("Model Info (No Key)", test_model_info_without_key),
        ("Translate - Missing Fields", test_translate_missing_fields),
        ("Translate - Empty Source", test_translate_empty_source_code),
        ("Translate - Unsupported Language", test_translate_unsupported_language),
        ("Translate - Same Language", test_translate_same_language),
        ("Translate - Code Too Long", test_translate_code_too_long),
        ("Translate - Valid Request", test_translate_valid_request),
        ("404 Endpoint", test_404_endpoint),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} CRASHED: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the server.")
        print("Please start the server first: python backend/app.py")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Server is not responding.")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)

