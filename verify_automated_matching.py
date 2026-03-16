#!/usr/bin/env python3
"""
Verify the automated matching platform is working correctly
"""

import requests
import json
import sys

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://localhost:3000"

print("=" * 60)
print("AUTOMATED MATCHING PLATFORM - VERIFICATION SCRIPT")
print("=" * 60)

# Check backend
print("\n1. Checking backend...")
try:
    response = requests.get(f"{API_BASE_URL}/../health", timeout=2)
    print("   ✅ Backend is running (port 8000)")
except:
    print("   ❌ Backend not running. Start with: python run_server.py")
    sys.exit(1)

# Check frontend
print("\n2. Checking frontend...")
try:
    response = requests.get(FRONTEND_URL, timeout=2)
    if response.status_code == 200:
        print("   ✅ Frontend is running (port 3000)")
except:
    print("   ❌ Frontend not running. Start with: npm run dev")

# Login test
print("\n3. Testing recruiter login...")
try:
    login_response = requests.post(
        f"{API_BASE_URL}/auth-simple/login",
        json={"email": "recruiter@example.com", "password": "Recruiter@1234"}
    )
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        print("   ✅ Recruiter login successful")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print("   Run: python create_all_test_accounts.py")
except Exception as e:
    print(f"   ❌ Login error: {str(e)}")
    sys.exit(1)

# Check recruiter's jobs
print("\n4. Checking recruiter's jobs...")
try:
    headers = {"Authorization": f"Bearer {token}"}
    jobs_response = requests.get(f"{API_BASE_URL}/jobs", headers=headers)
    
    if jobs_response.status_code == 200:
        jobs = jobs_response.json().get("data", [])
        print(f"   ✅ Found {len(jobs)} jobs")
        
        if jobs:
            for job in jobs[:3]:
                print(f"      • {job['title']} ({job['company']})")
        else:
            print("   ⚠️  No jobs found. Run: python create_test_data.py")
    else:
        print(f"   ❌ Failed to fetch jobs: {jobs_response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Check matches
print("\n5. Checking matches...")
try:
    if jobs:
        headers = {"Authorization": f"Bearer {token}"}
        matches_response = requests.get(
            f"{API_BASE_URL}/matches/job/{jobs[0]['id']}", 
            headers=headers
        )
        
        if matches_response.status_code == 200:
            matches = matches_response.json()
            if isinstance(matches, list):
                print(f"   ✅ Found {len(matches)} matches for job '{jobs[0]['title']}'")
                
                if matches:
                    match = matches[0]
                    print(f"\n   Sample Match:")
                    print(f"      Candidate: {match.get('candidate_name')}")
                    print(f"      Score: {(match.get('overall_score', 0) * 100):.0f}%")
                    print(f"      Semantic: {(match.get('semantic_similarity', 0) * 100):.1f}%")
                    print(f"      Skills: {(match.get('skill_overlap_score', 0) * 100):.1f}%")
                    print(f"      Experience: {(match.get('experience_alignment', 0) * 100):.1f}%")
            else:
                print(f"   ❌ Unexpected response format")
        else:
            print(f"   ❌ Failed to fetch matches: {matches_response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE!")
print("=" * 60)

print("\n✅ If all checks passed:")
print("   1. Open http://localhost:3000 in browser")
print("   2. Login: recruiter@example.com / Recruiter@1234")
print("   3. Navigate to Matches")
print("   4. See all jobs and matches automatically!")

print("\n❌ If some checks failed:")
print("   1. Run: python init_db_improved.py")
print("   2. Run: python create_test_data.py")
print("   3. Start backend: python run_server.py")
print("   4. Start frontend: npm run dev")
print("   5. Re-run this script")

print("\n" + "=" * 60)
