from app.core.database import SessionLocal
from app.models.match import Match
from app.models.candidate import Candidate
from app.api.v1.candidates import process_resume
from app.schemas.candidate import ProcessResumeRequest
from loguru import logger
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.getcwd())

def reset_matches():
    db = SessionLocal()
    try:
        # 1. Clear existing matches
        num_deleted = db.query(Match).delete()
        db.commit()
        print(f"Deleted {num_deleted} existing matches.")
        
        # 2. For each candidate, re-trigger process_resume to generate new matches with fixed logic
        candidates = db.query(Candidate).all()
        print(f"Re-processing {len(candidates)} candidates...")
        
        for candidate in candidates:
            if candidate.resume_file_path and os.path.exists(candidate.resume_file_path):
                print(f"  Re-processing {candidate.name}...")
                try:
                    # use process_resume synchronously
                    req = ProcessResumeRequest(file_path=candidate.resume_file_path)
                    res = process_resume(candidate.id, req, db)
                    print(f"    Done: {res.get('matches_generated', 0)} matches created.")
                except Exception as e:
                    print(f"    Error re-processing {candidate.name}: {e}")
            else:
                print(f"  Skipping {candidate.name} (no file path or file missing)")
                
    finally:
        db.close()

if __name__ == "__main__":
    reset_matches()
