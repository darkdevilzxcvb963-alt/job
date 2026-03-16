
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
email = "run12345@gmail.com"
user = db.query(User).filter(User.email == email).first()
candidate = db.query(Candidate).filter(Candidate.email == email).first()

print(f"User: {user.email if user else 'NOT FOUND'} | Role: {user.role if user else 'N/A'}")
print(f"Candidate Profile: {'FOUND' if candidate else 'NOT FOUND'}")
if candidate:
    print(f"Candidate ID: {candidate.id}")
    print(f"Has Embedding: {candidate.resume_embedding is not None}")
    matches = db.query(Match).filter(Match.candidate_id == candidate.id).all()
    print(f"Match Count: {len(matches)}")
    if matches:
        print(f"Sample Match Score: {matches[0].overall_score}")

db.close()
