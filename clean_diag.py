
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))
from app.core.database import SessionLocal
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.user import User

db = SessionLocal()
print(f"Total Candidates: {db.query(Candidate).count()}")
print(f"Candidates with Embeddings: {db.query(Candidate).filter(Candidate.resume_embedding != None).count()}")
print(f"Total Jobs: {db.query(Job).count()}")
print(f"Jobs with Embeddings: {db.query(Job).filter(Job.job_embedding != None).count()}")
print(f"Total Matches: {db.query(Match).count()}")

for r in db.query(User).filter(User.role == 'recruiter').all():
    job_count = db.query(Job).filter(Job.recruiter_id == r.id).count()
    print(f"Recruiter {r.email}: {job_count} jobs")

db.close()
