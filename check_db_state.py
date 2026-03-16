
import sys
from pathlib import Path
from sqlalchemy import create_all, text
from sqlalchemy.orm import Session

# Add backend to path
backend_dir = Path.cwd() / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine
from app.models.user import User, CandidateProfile, RecruiterProfile
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match

def check_counts():
    db = SessionLocal()
    try:
        users_count = db.query(User).count()
        candidate_profiles_count = db.query(CandidateProfile).count()
        candidates_count = db.query(Candidate).count()
        recruiters_count = db.query(RecruiterProfile).count()
        jobs_count = db.query(Job).count()
        matches_count = db.query(Match).count()
        
        print(f"Users: {users_count}")
        print(f"User CandidateProfiles: {candidate_profiles_count}")
        print(f"Resume Candidates: {candidates_count}")
        print(f"Recruiter Profiles: {recruiters_count}")
        print(f"Jobs: {jobs_count}")
        print(f"Matches: {matches_count}")
        
        if matches_count == 0 and jobs_count > 0 and candidates_count > 0:
            print("\nWARNING: We have jobs and resume candidates but ZERO matches. Match generation might have failed or not run.")
            
        # Check for embeddings
        jobs_with_embeddings = db.query(Job).filter(Job.job_embedding.isnot(None)).count()
        candidates_with_embeddings = db.query(Candidate).filter(Candidate.resume_embedding.isnot(None)).count()
        
        print(f"\nJobs with Embeddings: {jobs_with_embeddings}/{jobs_count}")
        print(f"Candidates with Embeddings: {candidates_with_embeddings}/{candidates_count}")
        
        if jobs_with_embeddings < jobs_count:
            print(f"ALERT: {jobs_count - jobs_with_embeddings} jobs are missing embeddings!")
        if candidates_with_embeddings < candidates_count:
            print(f"ALERT: {candidates_count - candidates_with_embeddings} candidates are missing embeddings!")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
