import os
import sys
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Force correct DB URL for root execution
os.environ["DATABASE_URL"] = "sqlite:///resume_matching.db"

from app.core.database import SessionLocal
from app.models.user import User, UserRole, CandidateProfile
from app.models.candidate import Candidate
from app.core.security import get_password_hash
from app.services.resume_parser import ResumeParser
from app.services.nlp_processor import NLPProcessor

def recover_users():
    print("Starting data recovery...")
    db = SessionLocal()
    parser = ResumeParser()
    # nlp = NLPProcessor() # Spacy model issues, skipping deep extraction
    
    uploads_dir = Path(os.getcwd()) / "backend" / "uploads"
    # Debug path
    print(f"Searching in: {uploads_dir.absolute()}")
    if not uploads_dir.exists():
        print("Uploads directory not found! (Absolute path check failed)")
        return

    count = 0
    files = list(uploads_dir.glob("*"))
    with open("debug_recovery.txt", "w", encoding="utf-8") as f:
        f.write(f"Directory: {uploads_dir}\n")
        f.write(f"Found {len(files)} files\n")
        
        for file_path in files:
            is_file = file_path.is_file()
            suffix = file_path.suffix.lower()
            f.write(f"Checking: {file_path.name}, is_file: {is_file}, suffix: {suffix}\n")
            
            if is_file and suffix in ['.pdf', '.docx']:
                f.write(f"MATCH: {file_path.name}\n")
                print(f"Recovering from: {file_path.name}")
            else:
                f.write(f"SKIP: {file_path.name}\n")
                continue
            try:
                # 1. Parse Resume
                parsed_data = parser.parse(str(file_path))
                text = parsed_data.get("text", "")
                
                filename_base = file_path.stem.replace(" ", "_").lower()
                email = f"recovered_{filename_base}_{uuid.uuid4().hex[:4]}@example.com"
                
                if db.query(User).filter(User.email == email).first():
                    f.write(f"SKIP: Duplicate email {email}\n")
                    print(f"Skipping duplicate email: {email}")
                    continue

                # 3. Create User
                user = User(
                    full_name=file_path.stem.replace("_", " ").title(),
                    email=email,
                    hashed_password=get_password_hash("Recovered@1234"),
                    role=UserRole.JOB_SEEKER,
                    is_verified=True,
                    is_active=True
                )
                db.add(user)
                db.flush()
                
                profile = CandidateProfile(
                    user_id=user.id,
                    headline="Recovered Profile",
                    years_of_experience=2
                )
                db.add(profile)
                
                # 5. Create Candidate (Resume)
                candidate = Candidate(
                    name=user.full_name,          # Derived from filename
                    email=user.email,             # Same as user email
                    resume_text=text,
                    resume_file_path=str(file_path.name),
                    skills=["Recovered"],         # JSON list
                    experience_years=0.0,         # Float
                    education=[],                 # JSON list
                    resume_file_type=file_path.suffix.lower().replace('.', '')
                )
                db.add(candidate)
                
                count += 1
                f.write(f"SUCCESS: Created user {user.email}\n")
                print(f"[SUCCESS] Created user: {user.email}")
                
            except Exception as e:
                f.write(f"ERROR: {file_path.name} - {str(e)}\n")
                import traceback
                f.write(traceback.format_exc() + "\n")
                print(f"[FAILED] Failed to recover {file_path.name}")
                print(f"Error details: {str(e)}")
                db.rollback()
                continue

    db.commit()
    print(f"Recovery complete. Recovered {count} users.")
    db.close()

if __name__ == "__main__":
    recover_users()
