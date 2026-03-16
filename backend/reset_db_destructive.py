"""
Initialize database with improved schema
"""
import os
import sys
# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine
from app.models.user import User, UserRole, CandidateProfile, RecruiterProfile
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.models.password_reset import PasswordReset
from app.models.user_session import UserSession
from app.core.security import get_password_hash
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create all tables
Base.metadata.create_all(bind=engine)

print("✓ Database tables created successfully!")

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Create test admin
    test_admin = db.query(User).filter(User.email == "admin@example.com").first()
    
    if not test_admin:
        test_admin = User(
            full_name="Admin User",
            email="admin@example.com",
            phone="9876543210",
            hashed_password=get_password_hash("Admin@1234"),
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=True,
            bio="Platform administrator",
            location="Headquarters"
        )
        db.add(test_admin)
        print("✓ Test admin created: admin@example.com")
    
    # Create test candidates
    test_candidate = db.query(User).filter(User.email == "candidate@example.com").first()
    
    if not test_candidate:
        test_candidate = User(
            full_name="John Doe",
            email="candidate@example.com",
            phone="1234567890",
            hashed_password=get_password_hash("Test@1234"),
            role=UserRole.JOB_SEEKER,
            is_verified=True,
            is_active=True,
            bio="Software developer with 5 years of experience",
            location="New York, USA"
        )
        db.add(test_candidate)
        db.flush()
        
        # Create candidate profile
        candidate_profile = CandidateProfile(
            user_id=test_candidate.id,
            headline="Full Stack Developer",
            years_of_experience=5,
            skills='["Python", "JavaScript", "React", "FastAPI", "PostgreSQL"]',
            expertise_areas='["Web Development", "Backend", "Frontend"]',
            preferred_locations='["New York", "Remote"]',
            preferred_job_types='["Full-time", "Remote"]',
            salary_expectation_min=100000,
            salary_expectation_max=150000,
            profile_completion_percentage=90
        )
        db.add(candidate_profile)
        print("✓ Test candidate created: candidate@example.com")
    
    # Create test recruiter
    test_recruiter = db.query(User).filter(User.email == "recruiter@example.com").first()
    
    if not test_recruiter:
        test_recruiter = User(
            full_name="Jane Smith",
            email="recruiter@example.com",
            phone="0987654321",
            hashed_password=get_password_hash("Test@1234"),
            role=UserRole.RECRUITER,
            is_verified=True,
            is_active=True,
            bio="HR Manager at Tech Company",
            location="San Francisco, USA"
        )
        db.add(test_recruiter)
        db.flush()
        
        # Create recruiter profile
        recruiter_profile = RecruiterProfile(
            user_id=test_recruiter.id,
            company_name="Tech Innovations Inc.",
            company_website="https://techinnovations.com",
            company_description="Leading software development company",
            company_size="medium",
            company_industry="Technology",
            job_title="Senior HR Manager",
            department="Human Resources",
            company_verified=True,
            total_jobs_posted=0,
            active_job_postings=0
        )
        db.add(recruiter_profile)
        print("✓ Test recruiter created: recruiter@example.com")
    
    db.commit()
    print("\n✓ Database initialization complete!")
    print("\nTest Accounts:")
    print("=" * 50)
    print("\nAdmin Account:")
    print("  Email: admin@example.com")
    print("  Password: Admin@1234")
    print("  Role: Admin")
    print("\nCandidate Account:")
    print("  Email: candidate@example.com")
    print("  Password: Test@1234")
    print("  Role: Job Seeker")
    print("\nRecruiter Account:")
    print("  Email: recruiter@example.com")
    print("  Password: Test@1234")
    print("  Role: Recruiter")
    print("\n" + "=" * 50)
    
except Exception as e:
    print(f"✗ Error initializing database: {str(e)}")
    db.rollback()
    raise
finally:
    db.close()
