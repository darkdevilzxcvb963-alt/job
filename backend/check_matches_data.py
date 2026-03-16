from app.core.database import SessionLocal
from app.models.match import Match
from app.models.candidate import Candidate
from app.models.user import User

def check_matches():
    db = SessionLocal()
    try:
        matches = db.query(Match).limit(10).all()
        print(f"Found {len(matches)} matches.")
        for m in matches:
            print(f"Match ID: {m.id}, Candidate ID: {m.candidate_id}, Job ID: {m.job_id}, Status: {m.status}")
            candidate = db.query(Candidate).filter(Candidate.id == m.candidate_id).first()
            if candidate:
                print(f"  Linked to Candidate: {candidate.name} ({candidate.email})")
                user = db.query(User).filter(User.email == candidate.email).first()
                if user:
                    print(f"    Linked to User: {user.email}, Role: {user.role}")
                else:
                    print(f"    NO USER FOUND for email {candidate.email}")
            else:
                print(f"  NO CANDIDATE FOUND for ID {m.candidate_id}")
    finally:
        db.close()

if __name__ == "__main__":
    check_matches()
