import requests

print("=" * 60)
print("Testing Complete Login Flow for All Roles")
print("=" * 60)

BASE = 'http://localhost:8000/api/v1'

test_accounts = [
    {
        'name': 'Jobseeker',
        'email': 'jobseeker@example.com',
        'password': 'Jobseeker@1234',
        'expected_role': 'job_seeker',
        'expected_redirect': '/candidate'
    },
    {
        'name': 'Recruiter',
        'email': 'recruiter@example.com',
        'password': 'Recruiter@1234',
        'expected_role': 'recruiter',
        'expected_redirect': '/jobs'
    },
    {
        'name': 'Admin',
        'email': 'admin@example.com',
        'password': 'Admin@1234',
        'expected_role': 'admin',
        'expected_redirect': '/admin'
    }
]

for account in test_accounts:
    print(f"\n{'=' * 60}")
    print(f"Testing {account['name']} Account")
    print(f"{'=' * 60}")
    
    creds = {
        'email': account['email'],
        'password': account['password']
    }
    
    # Test login endpoint
    print(f"Attempting login with {account['email']}...")
    r = requests.post(f"{BASE}/auth-simple/login", json=creds)
    
    if r.status_code != 200:
        print(f"❌ Login failed: {r.status_code}")
        print(f"   Error: {r.text}")
        continue
    
    data = r.json()
    user = data.get('user', {})
    user_role = user.get('role')
    
    print(f"✓ Login successful (HTTP {r.status_code})")
    print(f"  Full Name: {user.get('full_name')}")
    print(f"  Email: {user.get('email')}")
    print(f"  Role: {user_role}")
    print(f"  Is Verified: {user.get('is_verified')}")
    print(f"  Is Active: {user.get('is_active')}")
    
    # Verify role matches expected
    if user_role == account['expected_role']:
        print(f"  ✓ Role matches expected: {account['expected_role']}")
    else:
        print(f"  ❌ Role mismatch! Expected {account['expected_role']}, got {user_role}")
    
    # Verify token was returned
    if data.get('access_token'):
        print(f"  ✓ Access token received: {data['access_token'][:30]}...")
    else:
        print(f"  ❌ No access token in response")
    
    if data.get('refresh_token'):
        print(f"  ✓ Refresh token received: {data['refresh_token'][:30]}...")
    else:
        print(f"  ❌ No refresh token in response")
    
    # Frontend would redirect to:
    print(f"  → Frontend should redirect to: {account['expected_redirect']}")

print("\n" + "=" * 60)
print("All Tests Complete!")
print("=" * 60)
print("\nIf all accounts show ✓, login is working correctly.")
print("Check browser console for any JavaScript errors if issues persist.")
