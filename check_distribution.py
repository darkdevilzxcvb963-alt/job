
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

print("--- Data Distribution ---")
for r in db.query(User).filter(User.role == 'recruiter').all():
    jobs = db.query(Job).filter(Job.recruiter_id == r.id).all()
    job_ids = [j.id for j in jobs]
    match_count = db.query(Match).filter(Match.job_id.in_(job_ids)).count() if job_ids else 0
    print(f"Recruiter: {r.email} | Jobs: {len(jobs)} | Matches: {match_count}")

for a in db.query(User).filter(User.role == 'admin').all():
    print(f"Admin: {a.email}")

for js in db.query(User).filter(User.role == 'job_seeker').all():
    candidate = db.query(Candidate).filter(Candidate.email == js.email).first()
    match_count = db.query(Match).filter(Match.candidate_id == candidate.id).count() if candidate else 0
    print(f"Job Seeker: {js.email} | Match Count: {match_count}")

db.close()
