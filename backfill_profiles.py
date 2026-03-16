import sys
import os
from pathlib import Path

# Add backend to path
current_dir = Path(os.getcwd()) / 'backend'
sys.path.insert(0, str(current_dir))

from app.core.database import SessionLocal
from app.models.user import User, UserRole, CandidateProfile, RecruiterProfile

def backfill_profiles():
    db = SessionLocal()
    users = db.query(User).all()
    count = 0
    for user in users:
        if user.role == UserRole.JOB_SEEKER:
            if not user.candidate_profile:
                profile = CandidateProfile(user_id=user.id)
                db.add(profile)
                print(f"Backfilled CandidateProfile for {user.email}")
                count += 1
        elif user.role == UserRole.RECRUITER:
            if not user.recruiter_profile:
                profile = RecruiterProfile(user_id=user.id, company_name="My Company")
                db.add(profile)
                print(f"Backfilled RecruiterProfile for {user.email}")
                count += 1
    
    db.commit()
    db.close()
    print(f"Successfully backfilled {count} profiles.")

if __name__ == "__main__":
    backfill_profiles()
