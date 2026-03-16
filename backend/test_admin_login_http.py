import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_admin_login():
    print(f"Testing Login with Admin Credentials...")
    
    login_data = {
        "email": "admin@example.com",
        "password": "Admin@1234"
    }
    
    try:
        # Try primary auth endpoint
        print(f"Attempting POST {BASE_URL}/auth/login")
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            if "detail" in data:
                msg = f"ERROR DETAIL: {data['detail']}"
                print(msg)
                with open("error_log.txt", "w") as f:
                    f.write(msg)
            else:
                print(f"Response Body: {response.text[:200]}")
        except:
            print(f"Response Body: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ Login SUCCESSFUL")
        elif "An error occurred during signup" in response.text:
            print("❌ REPRODUCED: 'An error occurred during signup'")
        elif "An error occurred during login" in response.text:
            print("✅ Error handling working: 'An error occurred during login'")
        else:
            print(f"⚠️ Other response: {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_admin_login()
