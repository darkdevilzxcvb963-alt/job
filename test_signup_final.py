#!/usr/bin/env python
"""Test signup endpoint with detailed error handling"""
import sys
import time

# Give backend time to start
print("Waiting for backend to fully start...")
time.sleep(8)

import requests
import json

url = 'http://127.0.0.1:8000/api/v1/auth/signup'

# Test 1: Validation error (short phone)
print("\n=== Test 1: Validation Error ===")
r = requests.post(url, json={
    'full_name': 'Test',
    'email': 't@t.com',
    'phone': '123',
    'password': 'Pass',
    'role': 'job_seeker'
}, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code != 500:
    print("Response:", json.dumps(r.json(), indent=2))
else:
    print("Response text:", r.text)

# Test 2: Valid user creation
print("\n=== Test 2: Valid User Creation ===")
r = requests.post(url, json={
    'full_name': 'John Doe',
    'email': 'john@example.com',
    'phone': '1234567890',
    'password': 'SecurePass123',
    'role': 'job_seeker'
}, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    result = r.json()
    print(f"✓ SUCCESS! User created.")
    print(f"  ID: {result.get('id')}")
    print(f"  Email: {result.get('email')}")
    print(f"  Full Name: {result.get('full_name')}")
else:
    print(f"Error {r.status_code}:")
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(r.text)

# Test 3: Duplicate email
print("\n=== Test 3: Duplicate Email ===")
r = requests.post(url, json={
    'full_name': 'Jane Doe',
    'email': 'john@example.com',
    'phone': '9876543210',
    'password': 'AnotherPass123',
    'role': 'recruiter'
}, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 400:
    print(f"✓ Correctly rejected duplicate email")
    print(f"  Error: {r.json().get('detail')}")
else:
    print(f"Response: {r.json()}")

print("\n=== Tests Complete ===")
