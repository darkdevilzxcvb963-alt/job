import requests
import json

def test_google_auth_placeholder():
    url = "http://127.0.0.1:8000/api/v1/auth/google-auth"
    payload = {
        "id_token": "mock_token",
        "role": "job_seeker"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Testing {url} with mock token...")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        # We expect a 401 if the token is invalid (which mock_token is)
        # but a 500 would indicate a code crash.
        if response.status_code == 401:
            print("SUCCESS: Endpoint reached and returned 401 as expected for mock token.")
        else:
            print(f"RESULT: {response.text}")
    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    test_google_auth_placeholder()
