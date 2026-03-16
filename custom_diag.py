
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.user import User

db = SessionLocal()

try:
    data = {
        "users": db.query(User).count(),
        "job_seekers": db.query(User).filter(User.role == "job_seeker").count(),
        "recruiters": db.query(User).filter(User.role == "recruiter").count(),
        "jobs": db.query(Job).count(),
        "active_jobs": db.query(Job).filter(Job.is_active == True).count(),
        "jobs_with_embeddings": db.query(Job).filter(Job.job_embedding != None).count(),
        "jobs_with_recruiter": db.query(Job).filter(Job.recruiter_id != None).count(),
        "candidates": db.query(Candidate).count(),
        "candidates_with_embeddings": db.query(Candidate).filter(Candidate.resume_embedding != None).count(),
        "matches": db.query(Match).count()
    }
    
    # Get a sample recruiter ID
    recruiter = db.query(User).filter(User.role == "recruiter").first()
    data["sample_recruiter_id"] = recruiter.id if recruiter else None
    
    # Check jobs for the sample recruiter
    if recruiter:
        data["jobs_for_sample_recruiter"] = db.query(Job).filter(Job.recruiter_id == recruiter.id).count()
    
    print(json.dumps(data, indent=2))

finally:
    db.close()
