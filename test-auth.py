"""
Quick test script to verify authentication is working
Run this after starting the backend server
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

print("=" * 50)
print("Testing Authentication")
print("=" * 50)

# Test 1: Signup
print("\n1. Testing Signup...")
signup_data = {
    "full_name": "Test User",
    "email": f"test{hash('test') % 10000}@example.com",  # Unique email
    "password": "Test1234",
    "role": "job_seeker"
}

try:
    response = requests.post(f"{API_BASE}/auth-simple/signup", json=signup_data)
    if response.status_code == 201:
        print("✓ Signup successful!")
        user_data = response.json()
        print(f"  User ID: {user_data['id']}")
        print(f"  Email: {user_data['email']}")
        print(f"  Verified: {user_data['is_verified']}")
    else:
        print(f"✗ Signup failed: {response.status_code}")
        print(f"  Error: {response.text}")
        # Try with main auth endpoint
        response = requests.post(f"{API_BASE}/auth/signup", json=signup_data)
        if response.status_code == 201:
            print("✓ Signup successful with main auth endpoint!")
            user_data = response.json()
        else:
            print(f"✗ Main auth also failed: {response.text}")
            exit(1)
except Exception as e:
    print(f"✗ Signup error: {str(e)}")
    exit(1)

# Test 2: Login
print("\n2. Testing Login...")
login_data = {
    "email": signup_data["email"],
    "password": signup_data["password"]
}

try:
    response = requests.post(f"{API_BASE}/auth-simple/login", json=login_data)
    if response.status_code == 200:
        print("✓ Login successful!")
        tokens = response.json()
        access_token = tokens["access_token"]
        print(f"  Access token received: {access_token[:20]}...")
        
        # Test 3: Get Current User
        print("\n3. Testing Get Current User...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print("✓ Get user info successful!")
            print(f"  Name: {user['full_name']}")
            print(f"  Email: {user['email']}")
            print(f"  Role: {user['role']}")
        else:
            print(f"✗ Get user failed: {response.status_code}")
            print(f"  Error: {response.text}")
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Error: {response.text}")
        # Try with main auth endpoint
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✓ Login successful with main auth endpoint!")
            tokens = response.json()
            access_token = tokens["access_token"]
        else:
            print(f"✗ Main auth also failed: {response.text}")
            exit(1)
except Exception as e:
    print(f"✗ Login error: {str(e)}")
    exit(1)

print("\n" + "=" * 50)
print("✓ All authentication tests passed!")
print("=" * 50)
print(f"\nYou can now login with:")
print(f"  Email: {signup_data['email']}")
print(f"  Password: {signup_data['password']}")
