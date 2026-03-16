import requests

BASE = 'http://localhost:8000/api/v1/auth'

signup = {
    'full_name': 'Test User',
    'email': 'testuser@example.com',
    'password': 'Test1234',
    'role': 'job_seeker'
}

r = requests.post(f"{BASE}/signup", json=signup)
print('signup', r.status_code, r.text)

if r.status_code == 201:
    creds = {'email': 'testuser@example.com', 'password': 'Test1234'}
    r2 = requests.post(f"{BASE}/login", json=creds)
    print('login', r2.status_code, r2.text)
else:
    print('Signup failed; skipping login')
