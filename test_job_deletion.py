import requests
import json
import uuid

BASE_URL = "http://localhost:8001/api/v1"

def test_delete_job():
    # 1. Login as recruiter
    # Using a known recruiter email if possible, or creating one
    # For now, let's assume we can use the login API
    
    # Try to find a recruiter email from the database or use a common one
    # srihariharan26ias@gmail.com was mentioned in previous conversations as a user
    
    login_data = {
        "email": "srihariharan26ias@gmail.com",
        "password": "Password123" # Common test password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create a dummy job
        dummy_job = {
            "title": f"Temporary Test Job {uuid.uuid4().hex[:6]}",
            "company": "Test Corp",
            "description": "This is a temporary job for testing deletion.",
            "required_skills": ["Python", "Pytest"],
            "location": "Remote",
            "is_active": True
        }
        
        create_response = requests.post(f"{BASE_URL}/jobs/", json=dummy_job, headers=headers)
        if create_response.status_code != 201:
            print(f"Job creation failed: {create_response.status_code} {create_response.text}")
            return
        
        job_id = create_response.json()["id"]
        print(f"Created job with ID: {job_id}")
        
        # 3. Verify it exists
        get_response = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)
        if get_response.status_code == 200:
            print("Verified job exists.")
        
        # 4. Delete the job
        delete_response = requests.delete(f"{BASE_URL}/jobs/{job_id}", headers=headers)
        if delete_response.status_code == 204:
            print("Job deleted successfully (204 No Content).")
        else:
            print(f"Delete failed: {delete_response.status_code} {delete_response.text}")
            return
            
        # 5. Verify it's gone
        get_response_final = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)
        if get_response_final.status_code == 404:
            print("Verified job no longer exists (404 Not Found).")
        else:
            print(f"Wait, job still exists or returned {get_response_final.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_delete_job()
