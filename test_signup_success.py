import requests
import json
import uuid

def test_recruiter_signup_success():
    url = "http://localhost:8000/api/v1/auth/signup"
    # Use unique email and phone to avoid the previous error
    unique_id = str(uuid.uuid4())[:8]
    data = {
        "full_name": "Test Recruiter",
        "email": f"recruiter_{unique_id}@test.com",
        "phone": f"99{unique_id}00",
        "password": "Password123",
        "role": "recruiter"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_recruiter_signup_success()
