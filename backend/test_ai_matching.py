
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "uuid@test.com"
PASSWORD = "password123"

def test_matching():
    # 1. Login
    print("Logging in...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    auth_data = login_response.json()
    token = auth_data["access_token"]
    user_id = auth_data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Generate Matches
    print(f"Generating matches for user {user_id}...")
    gen_response = requests.post(
        f"{BASE_URL}/matches/generate-for-candidate/{user_id}",
        headers=headers
    )
    print(f"Gen status: {gen_response.status_code}")
    print(f"Gen results: {gen_response.json()}")
    
    # 3. Get Matches
    print("Fetching matches...")
    match_response = requests.get(f"{BASE_URL}/matches/my-matches", headers=headers)
    if match_response.status_code != 200:
        print(f"Fetch failed: {match_response.text}")
        return
    
    matches = match_response.json()
    print(f"Found {len(matches)} matches")
    
    if matches:
        m = matches[0]
        print(f"Match Score: {m.get('overall_score')}")
        print(f"AI Analysis (Explanation): {m.get('match_explanation')}")
        if not m.get('match_explanation'):
            print("FAILED: No AI analysis found in match record")
        else:
            print("SUCCESS: AI analysis is present")
    else:
        print("FAILED: No matches found for user")

if __name__ == "__main__":
    test_matching()
