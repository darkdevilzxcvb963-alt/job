import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash

DATABASE_URL = "postgresql://candidates:F3J5QY5ZYCztdJUFx59ZUIfDDsNLZyeH@dpg-d7s5pejeo5us73djctag-a.oregon-postgres.render.com/resume_05hg"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_or_update_user(db, email, password, role="job_seeker"):
    user = db.query(User).filter(User.email == email).first()
    hashed = get_password_hash(password)
    if user:
        user.hashed_password = hashed
        user.is_verified = True
        user.is_active = True
        user.mfa_enabled = False
        user.role = role
        print(f"Updated user: {email}")
    else:
        user = User(
            full_name=email.split('@')[0],
            email=email,
            username=email.split('@')[0],
            hashed_password=hashed,
            role=role,
            is_verified=True,
            is_active=True,
            mfa_enabled=False
        )
        db.add(user)
        print(f"Created new user: {email}")

def main():
    db = SessionLocal()
    try:
        print("Connecting to production database...")
        create_or_update_user(db, "jobseeker@example.com", "Jobseeker@1234", "job_seeker")
        create_or_update_user(db, "rassistant@gmail.com", "Assistant@123", "recruiter") 
        db.commit()
        print("Successfully added/updated users in production!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
