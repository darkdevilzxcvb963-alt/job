import requests
import json

base_url = "http://localhost:8001/api/v1"

def test_signup():
    url = f"{base_url}/auth/signup"
    payload = {
        "full_name": "Test User Unique",
        "email": "unique_user_99@example.com",
        "password": "Password123!",
        "role": "job_seeker",
        "phone": "9988776655"
    }
    
    print(f"Testing signup at {url}...")
    try:
        response = requests.post(url, json=payload)
        output = f"Status Code: {response.status_code}\nResponse Body: {response.text}"
        print(output)
        with open("signup_result.txt", "w") as f:
            f.write(output)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_signup()
