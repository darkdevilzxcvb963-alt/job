import requests
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "uuid@test.com"

def test_reset_flow():
    print(f"\n--- Testing Password Reset Flow for {TEST_EMAIL} ---")
    
    # 1. Request password reset
    print(f"1. Requesting password reset...")
    try:
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": TEST_EMAIL})
        if response.status_code != 200:
            print(f"   FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return
        
        data = response.json()
        print(f"   SUCCESS: {data.get('message')}")
        
        dev_link = data.get('dev_reset_link')
        if not dev_link:
            print("   WARNING: No dev_reset_link in response. Is this email in the database?")
            return
        
        token = dev_link.split("token=")[1]
        print(f"   TOKEN FOUND: {token[:10]}...")
        
        # 2. Validate token
        print(f"2. Validating token...")
        val_response = requests.post(f"{BASE_URL}/auth/validate-reset-token", json={"token": token})
        if val_response.status_code != 200:
            print(f"   FAILED: Status {val_response.status_code}")
            print(f"   Response: {val_response.text}")
            return
        
        val_data = val_response.json()
        if val_data.get("valid"):
            print(f"   SUCCESS: Token is valid. Expires in {val_data.get('expires_in_hours'):.2f} hours")
        else:
            print(f"   FAILED: Token reports as invalid")
            return
            
        # 3. Reset password
        print(f"3. Performing password reset...")
        reset_response = requests.post(f"{BASE_URL}/auth/reset-password", json={
            "token": token,
            "new_password": "NewPassword123"
        })
        
        if reset_response.status_code == 200:
            print(f"   SUCCESS: {reset_response.json().get('message')}")
        else:
            print(f"   FAILED: Status {reset_response.status_code}")
            print(f"   Response: {reset_response.text}")
            
    except Exception as e:
        print(f"   ERROR: {str(e)}")

if __name__ == "__main__":
    # Ensure backend is running before testing
    test_reset_flow()
