import os
import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.abspath('.'))

from app.main import app

def test_resume_endpoint():
    client = TestClient(app)
    
    # 1. Find a resume file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(base_dir, 'uploads')
    
    files = [f for f in os.listdir(uploads_dir) if f.endswith(('.pdf', '.docx'))]
    if not files:
        print("No resumes found to test with.")
        return
        
    test_file_path = os.path.join(uploads_dir, files[0])
    print(f"Testing with file: {test_file_path}")
    
    # 2. Create a dummy candidate
    unique_email = f"test_candidate_{uuid.uuid4().hex[:8]}@example.com"
    candidate_data = {
        "name": "Test Candidate",
        "email": unique_email,
        "phone": "1234567890"
    }
    
    print("Creating candidate...")
    response = client.post("/api/v1/candidates/", json=candidate_data)
    if response.status_code != 201:
        print(f"Failed to create candidate: {response.text}")
        return
        
    candidate_id = response.json()["id"]
    print(f"Candidate created: {candidate_id}")
    
    # 3. Call process-resume endpoint
    print("Processing resume...")
    payload = {"file_path": test_file_path}
    
    # Note: process-resume expects absolute path or relative to cwd?
    # The code verifies file existence.
    
    response = client.post(f"/api/v1/candidates/{candidate_id}/process-resume", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS: Resume processed via API")
        print(f"Skills extracted: {data.get('skills_extracted')}")
        print(f"Categories found: {list(data.get('skills_by_category', {}).keys())}")
        
        # Verify db update
        cand_response = client.get(f"/api/v1/candidates/{candidate_id}")
        cand_data = cand_response.json()
        saved_skills = cand_data.get("skills")
        if saved_skills:
             print("Verification: Skills persisted to DB.")
        else:
             print("WARNING: Skills not persisted to DB?")
             
    else:
        print(f"FAILURE: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_resume_endpoint()
