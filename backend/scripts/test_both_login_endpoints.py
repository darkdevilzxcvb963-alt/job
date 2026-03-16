import requests

BASE = 'http://localhost:8000/api/v1'

# Test auth-simple login (frontend uses this)
creds = {'email': 'admin@example.com', 'password': 'Admin@1234'}
r = requests.post(f"{BASE}/auth-simple/login", json=creds)
print('auth-simple/login status:', r.status_code)
print(r.text[:500])

# Test regular auth login too
r2 = requests.post(f"{BASE}/auth/login", json=creds)
print('\nauth/login status:', r2.status_code)
print(r2.text[:500])
