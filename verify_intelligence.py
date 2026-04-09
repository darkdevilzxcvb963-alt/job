import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_intelligence_endpoints():
    print("--- Testing Intelligence Endpoints ---")
    
    # These endpoints require authentication, but we can verify their presence and basic schema
    # via the docs or by checking if they return 401/403 (unauthorized) instead of 404 (not found)
    
    endpoints = [
        "/intelligence/completeness",
        "/intelligence/suggestions"
    ]
    
    for ep in endpoints:
        print(f"Checking {ep}...")
        try:
            response = requests.get(f"{BASE_URL}{ep}")
            # We expect 401/403 since no auth is provided, but this confirms the route is registered
            if response.status_code in [401, 403]:
                print(f"SUCCESS: Route {ep} is registered and protected.")
            elif response.status_code == 404:
                 print(f"FAILED: Route {ep} not found (404).")
            else:
                print(f"INFO: Route {ep} returned {response.status_code}")
        except Exception as e:
            print(f"ERROR: Could not connect to {ep}: {e}")

    # For skill gaps, we need a job_id
    print("\nChecking Skill Gaps registration...")
    try:
        response = requests.get(f"{BASE_URL}/intelligence/gaps/test-job-id")
        if response.status_code in [401, 403]:
            print("SUCCESS: Skill Gaps route is registered and protected.")
        elif response.status_code == 404:
            print("FAILED: Skill Gaps route not found (404).")
        else:
            print(f"INFO: Skill Gaps route returned {response.status_code}")
    except Exception as e:
        print(f"ERROR: Could not connect to skill gaps: {e}")

if __name__ == "__main__":
    test_intelligence_endpoints()
