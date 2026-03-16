import requests
import sys

def check_backend():
    base_url = "http://127.0.0.1:8000"
    health_url = f"{base_url}/health"
    google_auth_url = f"{base_url}/api/v1/auth/google-auth"

    try:
        # Check Health
        print(f"Checking backend health at {health_url}...")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("Backend is running and healthy.")
        else:
            print(f"Backend returned status {response.status_code}: {response.text}")
            return False

        # Check CORS
        print(f"\nChecking CORS for {google_auth_url}...")
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
        response = requests.options(google_auth_url, headers=headers, timeout=5)
        
        print(f"OPTIONS Response Code: {response.status_code}")
        print("Response Headers:")
        for k, v in response.headers.items():
            if "access-control" in k.lower():
                print(f"  {k}: {v}")
        
        if "access-control-allow-origin" in [k.lower() for k in response.headers.keys()]:
            print("CORS headers present.")
        else:
            print("WARNING: CORS headers missing!")
            return False

        return True

    except requests.exceptions.ConnectionError:
        print("ERROR: Connection failed. Is the backend running?")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = check_backend()
    if not success:
        sys.exit(1)
