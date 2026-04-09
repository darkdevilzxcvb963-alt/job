import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_privacy_endpoints():
    print("--- Testing Privacy Endpoints ---")
    
    # 1. Test Privacy Policy
    print("Checking Privacy Policy...")
    response = requests.get(f"{BASE_URL}/privacy/privacy-policy")
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: Title: {data.get('title')}")
    else:
        print(f"FAILED: Status {response.status_code}")

    # Note: Export and Deletion require authentication.
    # In a real test environment, we would log in first.
    # Since this is a live environment review, we'll check headers on the public endpoint.
    
    print("\nChecking Security Headers...")
    headers = response.headers
    expected_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    for h, val in expected_headers.items():
        if headers.get(h) == val:
            print(f"SUCCESS: {h}: {val}")
        else:
            print(f"FAILED: {h} is {headers.get(h)} (Expected {val})")

if __name__ == "__main__":
    try:
        test_privacy_endpoints()
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Ensure the backend server is running on http://localhost:8000")
