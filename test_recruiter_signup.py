import requests

url = "http://localhost:8000/api/v1/auth/signup"
data = {
    "full_name": "Test Recruiter",
    "email": "recruiter_test@example.com",
    "password": "TestPassword123",
    "role": "recruiter",
    "phone": "1234567890"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
