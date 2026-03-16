import requests

BASE = 'http://localhost:8000/api/v1'

# Create jobseeker account
print("Creating jobseeker account...")
jobseeker_signup = {
    'full_name': 'John Doe',
    'email': 'jobseeker@example.com',
    'password': 'Jobseeker@1234',
    'role': 'job_seeker'
}
r = requests.post(f"{BASE}/auth-simple/signup", json=jobseeker_signup)
print(f"Signup status: {r.status_code}")
if r.status_code != 201:
    print(f"Error: {r.text}")
else:
    print("✓ Jobseeker account created")

# Test jobseeker login
print("\nTesting jobseeker login...")
creds = {'email': 'jobseeker@example.com', 'password': 'Jobseeker@1234'}
r = requests.post(f"{BASE}/auth-simple/login", json=creds)
print(f"Login status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"✓ Jobseeker login successful")
    print(f"  User: {data['user']['full_name']}")
    print(f"  Role: {data['user']['role']}")
    print(f"  Token: {data['access_token'][:30]}...")
else:
    print(f"✗ Login failed: {r.text}")

# Create recruiter account
print("\nCreating recruiter account...")
recruiter_signup = {
    'full_name': 'Jane Smith',
    'email': 'recruiter@example.com',
    'password': 'Recruiter@1234',
    'role': 'recruiter',
    'company_name': 'Tech Corp'
}
r = requests.post(f"{BASE}/auth-simple/signup", json=recruiter_signup)
print(f"Signup status: {r.status_code}")
if r.status_code != 201:
    print(f"Error: {r.text}")
else:
    print("✓ Recruiter account created")

# Test recruiter login
print("\nTesting recruiter login...")
creds = {'email': 'recruiter@example.com', 'password': 'Recruiter@1234'}
r = requests.post(f"{BASE}/auth-simple/login", json=creds)
print(f"Login status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"✓ Recruiter login successful")
    print(f"  User: {data['user']['full_name']}")
    print(f"  Role: {data['user']['role']}")
    print(f"  Token: {data['access_token'][:30]}...")
else:
    print(f"✗ Login failed: {r.text}")

print("\n" + "="*50)
print("Test Accounts Created:")
print("="*50)
print("\nJobSeeker:")
print("  Email: jobseeker@example.com")
print("  Password: Jobseeker@1234")
print("\nRecruiter:")
print("  Email: recruiter@example.com")
print("  Password: Recruiter@1234")
print("\nAdmin:")
print("  Email: admin@example.com")
print("  Password: Admin@1234")
