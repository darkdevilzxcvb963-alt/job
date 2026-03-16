import requests
import uuid
import json
import random

def diagnose_signup():
    unique_id = str(uuid.uuid4())[:8]
    # Use ONLY digits for phone
    phone = "".join([str(random.randint(0, 9)) for _ in range(10)])
    data = {
        "full_name": "Test Recruiter",
        "email": f"recruiter_{unique_id}@test.com",
        "phone": phone,
        "password": "Password123",
        "role": "recruiter"
    }
    
    url = 'http://localhost:8000/api/v1/auth/signup'
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    diagnose_signup()
