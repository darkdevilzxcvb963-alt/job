
import sys
import os
import json
import httpx
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

from app.core.security import create_access_token
from app.core.config import settings

def verify():
    # Recruiter Info (from my earlier audit)
    # recruiterhiring56@gmail.com
    recruiter_id = "9ebfe63e-fcae-4ae4-a251-2fa9691ee9bb"
    
    # 1. Generate token
    token = create_access_token(data={"sub": recruiter_id, "role": "recruiter"})
    print(f"Generated token for recruiter: {token[:20]}...")
    
    # 2. Call API
    api_url = "http://localhost:8000/api/v1/matches/recruiter-matches"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = httpx.get(api_url, headers=headers)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            matches = response.json()
            print(f"Total Matches found: {len(matches)}")
            for m in matches[:3]:
                print(f" - Match: {m['candidate_name']} <-> {m['job_title']} (Score: {m['overall_score']:.3f})")
            
            if len(matches) > 0:
                print("\nSUCCESS: Matches are correctly returned by the API for the recruiter.")
            else:
                print("\nWARNING: API returned 0 matches for this recruiter ID despite manual DB insert.")
        else:
            print(f"Error Details: {response.text}")
            
    except Exception as e:
        print(f"Error calling API: {e}")

if __name__ == "__main__":
    verify()
