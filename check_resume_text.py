
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))
from app.core.database import SessionLocal
from app.models.candidate import Candidate

db = SessionLocal()
email = "run12345@gmail.com"
candidate = db.query(Candidate).filter(Candidate.email == email).first()

if candidate:
    print(f"Candidate: {candidate.email}")
    print(f"Resume Text Length: {len(candidate.resume_text) if candidate.resume_text else 'None'}")
    print(f"Resume Path: {candidate.resume_file_path}")

db.close()
