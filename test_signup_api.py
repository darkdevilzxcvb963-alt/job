import requests
import json

print("Testing Signup API...")
print("=" * 60)

url = 'http://127.0.0.1:8000/api/v1/auth/signup'
data = {
    'full_name': 'Test User',
    'email': 'test@example.com',
    'phone': '1234567890',
    'password': 'TestPass123',
    'role': 'job_seeker'
}

try:
    print(f"POST {url}")
    response = requests.post(url, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {str(e)}")
