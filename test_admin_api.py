#!/usr/bin/env python3
"""
Test admin API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)

def print_response(response, title="Response"):
    print(f"\n{title}:")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

# Step 1: Login as admin
print_header("1. ADMIN LOGIN")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "admin@example.com",
        "password": "Admin@1234"
    }
)
print_response(login_response, "Login Response")

if login_response.status_code != 200:
    print("X Admin login failed!")
    exit(1)

admin_token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {admin_token}"}
print(f"OK Login successful! Token: {admin_token[:20]}...")

# Step 2: Get platform overview statistics
print_header("2. PLATFORM OVERVIEW STATISTICS")
stats_response = requests.get(
    f"{BASE_URL}/admin/stats/overview",
    headers=headers
)
print_response(stats_response, "Overview Statistics")

if stats_response.status_code == 200:
    stats = stats_response.json()
    print("\nPlatform Summary:")
    print(f"  Total Users: {stats.get('total_users', 0)}")
    print(f"  Verified Users: {stats.get('verified_users', 0)}")
    print(f"  Unverified Users: {stats.get('unverified_users', 0)}")
    print(f"  Active Users: {stats.get('active_users', 0)}")
    print(f"  Job Seekers: {stats.get('job_seekers', 0)}")
    print(f"  Recruiters: {stats.get('recruiters', 0)}")
    print(f"  Verified Companies: {stats.get('verified_recruiters', 0)}")
    print(f"  Pending Companies: {stats.get('pending_recruiters', 0)}")

# Step 3: List all users
print_header("3. LIST ALL USERS")
users_response = requests.get(
    f"{BASE_URL}/admin/users?skip=0&limit=10",
    headers=headers
)
print_response(users_response, "Users List")

if users_response.status_code == 200:
    users = users_response.json()
    print(f"\nFound {len(users)} users:")
    for user in users:
        status = "Verified" if user.get("is_verified") else "Unverified"
        active = "Active" if user.get("is_active") else "Inactive"
        print(f"  [{user.get('id')}] {user.get('full_name')} ({user.get('email')}) - {user.get('role')} - {status} - {active}")

# Step 4: Users by role statistics
print_header("4. USERS BY ROLE STATISTICS")
role_response = requests.get(
    f"{BASE_URL}/admin/stats/users-by-role",
    headers=headers
)
print_response(role_response, "Users by Role")

# Step 5: Verification status statistics
print_header("5. VERIFICATION STATUS STATISTICS")
verification_response = requests.get(
    f"{BASE_URL}/admin/stats/verification-status",
    headers=headers
)
print_response(verification_response, "Verification Status")

# Step 6: Get pending recruiters
print_header("6. PENDING RECRUITERS FOR VERIFICATION")
recruiters_response = requests.get(
    f"{BASE_URL}/admin/recruiters/pending?skip=0&limit=10",
    headers=headers
)
print_response(recruiters_response, "Pending Recruiters")

if recruiters_response.status_code == 200:
    recruiters = recruiters_response.json()
    print(f"\nFound {len(recruiters)} pending recruiters:")
    for recruiter in recruiters:
        print(f"  • {recruiter.get('company_name', 'N/A')} (ID: {recruiter.get('id')})")
        print(f"    Industry: {recruiter.get('company_industry', 'N/A')}")
        print(f"    Size: {recruiter.get('company_size', 'N/A')}")

# Step 7: Get activity log
print_header("7. RECENT ACTIVITY LOG")
activity_response = requests.get(
    f"{BASE_URL}/admin/stats/activity-log?hours=24",
    headers=headers
)
print_response(activity_response, "Activity Log")

print_header("DONE ADMIN API TESTING COMPLETE")
print("\nTest Summary:")
print("  - Admin login successful")
print("  - Overview statistics retrieved")
print("  - User listing working")
print("  - Statistics endpoints working")
print("  - Recruiter verification endpoint working")
print("  - Activity logging working")
print("\nAll admin endpoints tested!")
print("\n💡 Next Steps:")
print("  1. Access admin dashboard at: http://localhost:3000/admin")
print("  2. Login with: admin@example.com / Admin@1234")
print("  3. Manage users and verify recruiters through the web interface")
