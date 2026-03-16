import requests
res = requests.post("http://localhost:8000/api/v1/auth/login", json={
    "email": "uuid@test.com",
    "password": "TestPassword123"
})
print(f"Status: {res.status_code}")
print(f"Body: {res.text}")
