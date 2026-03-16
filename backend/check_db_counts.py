from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from sqlalchemy import func

def check_counts():
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        job_seekers = db.query(User).filter(User.role == UserRole.JOB_SEEKER.value).count()
        recruiters = db.query(User).filter(User.role == UserRole.RECRUITER.value).count()
        total_candidates = db.query(Candidate).count()
        candidates_with_resumes = db.query(Candidate).filter(Candidate.resume_file_path != None).count()
        
        # Check for candidates without users
        candidate_emails = [c.email for c in db.query(Candidate.email).all()]
        user_emails = [u.email for u in db.query(User.email).all()]
        
        candidates_no_user = [email for email in candidate_emails if email not in user_emails]
        users_no_candidate = [email for email in user_emails if email not in candidate_emails and db.query(User).filter(User.email == email).first().role == UserRole.JOB_SEEKER.value]
        
        print(f"Total Users: {total_users}")
        print(f"  Job Seekers (Users): {job_seekers}")
        print(f"  Recruiters (Users): {recruiters}")
        print(f"Total Candidates (Candidate Table): {total_candidates}")
        print(f"  Candidates with Resumes: {candidates_with_resumes}")
        print(f"Candidates without User record: {len(candidates_no_user)}")
        print(f"Job Seekers without Candidate record: {len(users_no_candidate)}")
        
        if candidates_no_user:
            print("\nFirst 5 candidates without users:")
            for email in candidates_no_user[:5]:
                print(f" - {email}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
