"""
Script to simulate the Recruiter Dashboard data fetching flow.
1. Login as recruiter
2. Fetch Jobs
3. Fetch Matches for each job
4. Report counts
"""
import requests
import json
import sys

"""
Script to simulate the Recruiter Dashboard data fetching flow using TestClient.
This allows us to see backend logs directly in the output.
"""
from fastapi.testclient import TestClient
from app.main import app
import sys

def run_simulation():
    print("="*60)
    print("RECRUITER DASHBOARD SIMULATION (TestClient)")
    print("="*60)

    client = TestClient(app)

    # 1. Login
    print("Logging in as Admin...")
    resp = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "Admin@1234"})
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} {resp.text}")
        return
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Logged in")

    # 2. Fetch Jobs
    print("\n[STEP 1] Fetching Jobs...")
    resp = client.get("/api/v1/jobs/", headers=headers)
    if resp.status_code != 200:
        print(f"❌ Failed to fetch jobs: {resp.status_code} {resp.text}")
        return
    
    jobs = resp.json()
    print(f"✓ Found {len(jobs)} jobs")
    if not jobs:
        print("No jobs found. Exiting.")
        return

    # 3. Fetch Matches for the first few jobs
    print("\n[STEP 2] Fetching Matches for up to 3 jobs (min_score=0.0)...")
    
    for job in jobs[:3]:
        job_id = job['id']
        print(f"\n--- Checking Job: {job['title']} (ID: {job_id}) ---")
        
        resp = client.get(
            f"/api/v1/matches/job/{job_id}", 
            params={"min_score": 0.0, "limit": 100},
            headers=headers
        )
        
        if resp.status_code != 200:
            print(f"   ❌ Failed to fetch matches: {resp.status_code} {resp.text}")
            continue
            
        matches = resp.json()
        print(f"   ✓ API returned {len(matches)} matches")

    print("\n" + "="*60)

if __name__ == "__main__":
    run_simulation()

