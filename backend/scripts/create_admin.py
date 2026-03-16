import requests

BASE = 'http://localhost:8000/api/v1/auth'
payload = {
    'full_name': 'Admin User',
    'email': 'admin@example.com',
    'password': 'Admin@1234',
    'role': 'admin'
}

r = requests.post(f"{BASE}/signup", json=payload)
print('status', r.status_code)
print(r.text)

if r.status_code == 201:
    print('Admin created')
else:
    print('Admin creation failed')
