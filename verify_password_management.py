import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_password_features():
    print("\n--- Testing Password Management Features ---")
    
    # 1. Login to get token (Admin)
    print("1. Logging in as admin...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "apitest@example.com",
        "password": "TestPassword123"
    })
    
    if login_res.status_code != 200:
        print(f"   FAILED: Admin login. Status {login_res.status_code}")
        return
    
    admin_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    print("   SUCCESS: Admin logged in")

    # 2. Get a user ID to reset
    print("2. Fetching users list...")
    users_res = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    if users_res.status_code != 200:
        print(f"   FAILED: Fetch users. Status {users_res.status_code}")
        return
    
    users = users_res.json()
    test_user = next((u for u in users if u["email"] == "uuid@test.com"), None)
    if not test_user:
        print("   FAILED: Could not find uuid@test.com in database")
        return
    
    user_id = test_user["id"]
    print(f"   SUCCESS: Found target user ID: {user_id}")

    # 3. Admin Reset Password
    print(f"3. Admin resetting password for {user_id}...")
    reset_res = requests.post(f"{BASE_URL}/admin/users/{user_id}/reset-password", 
                              json={"new_password": "NewAdminPassword123"},
                              headers=headers)
    
    if reset_res.status_code == 200:
        print(f"   SUCCESS: {reset_res.json()['message']}")
    else:
        print(f"   FAILED: Reset password. Status {reset_res.status_code}")
        print(f"   Response: {reset_res.text}")
        return

    # 4. User Change Password (Login as target user first)
    print("4. Testing User Change Password...")
    user_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "uuid@test.com",
        "password": "NewAdminPassword123"
    })
    
    if user_login.status_code != 200:
        print("   FAILED: Target user login with reset password")
        return
        
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    change_res = requests.post(f"{BASE_URL}/auth/change-password",
                               json={
                                   "current_password": "NewAdminPassword123",
                                   "new_password": "UserChosenPassword123"
                               },
                               headers=user_headers)
                               
    if change_res.status_code == 200:
        print(f"   SUCCESS: {change_res.json()['message']}")
    else:
        print(f"   FAILED: Change password. Status {change_res.status_code}")
        print(f"   Response: {change_res.text}")

if __name__ == "__main__":
    test_password_features()
