#!/usr/bin/env python
"""
Test admin login via API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("\n" + "="*60)
print("TESTING ADMIN LOGIN")
print("="*60)

credentials = {
    "email": "admin@example.com",
    "password": "Admin@1234"
}

print(f"\nAttempting login with:")
print(f"  Email: {credentials['email']}")
print(f"  Password: {credentials['password']}")
print(f"\nAPI Endpoint: {BASE_URL}/auth-simple/login")

try:
    response = requests.post(
        f"{BASE_URL}/auth-simple/login",
        json=credentials,
        timeout=5
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ LOGIN SUCCESSFUL!")
        print("="*60)
        print(f"User: {data['user']['full_name']}")
        print(f"Email: {data['user']['email']}")
        print(f"Role: {data['user']['role']}")
        print(f"Token: {data['access_token'][:50]}...")
        print("="*60)
        print("\n✅ Admin credentials are working!")
        print("\nYou can now log in at: http://localhost:3000/login")
    else:
        print(f"\n❌ LOGIN FAILED!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to backend server!")
    print("Make sure the backend is running at http://localhost:8000")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
