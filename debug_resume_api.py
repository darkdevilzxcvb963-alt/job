import requests
import json
import os

API_URL = "http://127.0.0.1:8000/api/v1"

def debug_api():
    # 1. Create dummy resume
    with open("dummy_resume.docx", "w") as f:
        f.write("This is a test resume with Python and React skills.")
    
    # 2. Upload Resume
    print("Uploading resume...")
    files = {'file': ('dummy_resume.docx', open('dummy_resume.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    try:
        upload_resp = requests.post(f"{API_URL}/upload/resume", files=files)
        print(f"Upload Status: {upload_resp.status_code}")
        print(f"Upload Response: {upload_resp.text}")
        
        if upload_resp.status_code != 200:
            return
            
        file_path = upload_resp.json()['file_path']
        
        # 3. Create Candidate (Dummy)
        # Note: In a real scenario we'd need a user token, but for this test 
        # let's assume we can hit the endpoint or just test the processing logic if capable.
        # Actually, let's just hit the process endpoint assuming we have a candidate_id.
        # We might need to look up a candidate first. 
        
        # For this quick debug, let's just try to hit the process endpoint with a potentially valid candidate ID 
        # or fail if we cant.
        
        print("\nNOTE: This script assumes a candidate exists. If 404, we need to create one first.")
        # Let's try to get a candidate
        get_cand = requests.get(f"{API_URL}/candidates")
        if get_cand.status_code == 200 and len(get_cand.json()) > 0:
            candidate_id = get_cand.json()[0]['id']
            print(f"Using Candidate ID: {candidate_id}")
            
            # 4. Process Resume
            print(f"Processing resume for {candidate_id}...")
            process_resp = requests.post(
                f"{API_URL}/candidates/{candidate_id}/process-resume",
                params={"file_path": file_path}
            )
            print(f"Process Status: {process_resp.status_code}")
            print(f"Process Response: {process_resp.text}")
        else:
            print("No candidates found to test with.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists("dummy_resume.docx"):
            os.remove("dummy_resume.docx")

if __name__ == "__main__":
    debug_api()
