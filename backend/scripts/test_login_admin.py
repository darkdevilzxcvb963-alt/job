import requests
url = 'http://localhost:8000/api/v1/auth/login'
creds = {'email': 'admin@example.com', 'password': 'Admin@1234'}
resp = requests.post(url, json=creds)
print('status', resp.status_code)
print(resp.text)
