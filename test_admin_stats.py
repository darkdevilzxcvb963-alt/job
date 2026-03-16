import requests
import json
import sqlite3
import os
from datetime import datetime, timedelta
import jwt

# Mock settings for token generation
SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Generate token for the admin user
admin_email = "srihariharan96ias@gmail.com"
token = create_access_token({"sub": admin_email})

print(f"Testing with token for {admin_email}")

try:
    response = requests.get(
        "http://localhost:8000/api/v1/admin/stats/overview",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error connecting to backend: {e}")
