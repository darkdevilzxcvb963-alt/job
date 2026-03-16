"""
Create test jobs and candidates for testing the matching system
"""
import sys
sys.path.insert(0, '/root/backend')

from app.core.database import SessionLocal
from app.models.user import User, UserRole, CandidateProfile, RecruiterProfile
from app.models.job import Job
from app.models.match import Match
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import json

db = SessionLocal()

try:
    # Get or create recruiter
    recruiter = db.query(User).filter(User.email == "recruiter@example.com").first()
    if not recruiter:
        print("✗ Recruiter not found. Create recruiter first!")
        sys.exit(1)
    
    # Get or create candidates
    candidate1 = db.query(User).filter(User.email == "jobseeker@example.com").first()
    if not candidate1:
        candidate1 = User(
            full_name="Alice Johnson",
            email="jobseeker@example.com",
            phone="5551234567",
            hashed_password=get_password_hash("Jobseeker@1234"),
            role=UserRole.JOB_SEEKER,
            is_verified=True,
            is_active=True,
            bio="Full Stack Developer",
            location="San Francisco, USA"
        )
        db.add(candidate1)
        db.flush()
    
    # Create candidate profile if not exists
    candidate1_profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == candidate1.id).first()
    if not candidate1_profile:
        candidate1_profile = CandidateProfile(
            user_id=candidate1.id,
            headline="Full Stack Developer",
            years_of_experience=6,
            skills=json.dumps(["Python", "JavaScript", "React", "FastAPI", "PostgreSQL", "Docker", "AWS"]),
            expertise_areas=json.dumps(["Web Development", "Backend", "Frontend", "DevOps"]),
            preferred_locations=json.dumps(["San Francisco", "Remote"]),
            preferred_job_types=json.dumps(["Full-time", "Remote"]),
            salary_expectation_min=120000,
            salary_expectation_max=180000,
            profile_completion_percentage=95
        )
        db.add(candidate1_profile)
        db.flush()
    
    # Create second candidate
    candidate2 = db.query(User).filter(User.email == "bob.engineer@example.com").first()
    if not candidate2:
        candidate2 = User(
            full_name="Bob Martinez",
            email="bob.engineer@example.com",
            phone="5559876543",
            hashed_password=get_password_hash("Bob@1234"),
            role=UserRole.JOB_SEEKER,
            is_verified=True,
            is_active=True,
            bio="Senior Backend Engineer",
            location="New York, USA"
        )
        db.add(candidate2)
        db.flush()
    
    candidate2_profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == candidate2.id).first()
    if not candidate2_profile:
        candidate2_profile = CandidateProfile(
            user_id=candidate2.id,
            headline="Senior Backend Engineer",
            years_of_experience=8,
            skills=json.dumps(["Python", "Java", "FastAPI", "Django", "PostgreSQL", "MongoDB", "Kubernetes"]),
            expertise_areas=json.dumps(["Backend Development", "Database Design", "System Architecture"]),
            preferred_locations=json.dumps(["New York", "Remote", "Boston"]),
            preferred_job_types=json.dumps(["Full-time"]),
            salary_expectation_min=150000,
            salary_expectation_max=200000,
            profile_completion_percentage=90
        )
        db.add(candidate2_profile)
        db.flush()
    
    # Create third candidate (partial match)
    candidate3 = db.query(User).filter(User.email == "sarah.designer@example.com").first()
    if not candidate3:
        candidate3 = User(
            full_name="Sarah Chen",
            email="sarah.designer@example.com",
            phone="5555551234",
            hashed_password=get_password_hash("Sarah@1234"),
            role=UserRole.JOB_SEEKER,
            is_verified=True,
            is_active=True,
            bio="UI/UX Designer",
            location="Los Angeles, USA"
        )
        db.add(candidate3)
        db.flush()
    
    candidate3_profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == candidate3.id).first()
    if not candidate3_profile:
        candidate3_profile = CandidateProfile(
            user_id=candidate3.id,
            headline="UI/UX Designer",
            years_of_experience=4,
            skills=json.dumps(["Figma", "Adobe XD", "CSS", "HTML", "React", "Design Systems"]),
            expertise_areas=json.dumps(["UI Design", "UX Design", "Design Systems", "Frontend"]),
            preferred_locations=json.dumps(["Los Angeles", "Remote"]),
            preferred_job_types=json.dumps(["Full-time", "Contract"]),
            salary_expectation_min=80000,
            salary_expectation_max=130000,
            profile_completion_percentage=85
        )
        db.add(candidate3_profile)
        db.flush()
    
    db.commit()
    print("✓ Candidates created successfully!")
    
    # Create test jobs for recruiter
    job1 = db.query(Job).filter(Job.title == "Senior Full Stack Developer").first()
    if not job1:
        job1 = Job(
            title="Senior Full Stack Developer",
            company="Tech Innovations Inc.",
            description="We are looking for a Senior Full Stack Developer with 6+ years of experience. You will work on scalable web applications using modern technologies.",
            required_skills=["Python", "JavaScript", "React", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            location="San Francisco, CA",
            job_type="Full-time",
            experience_required=6,
            salary_min=140000,
            salary_max=200000,
            is_active=True
        )
        db.add(job1)
        db.flush()
    
    job2 = db.query(Job).filter(Job.title == "Backend Engineer").first()
    if not job2:
        job2 = Job(
            title="Backend Engineer",
            company="Tech Innovations Inc.",
            description="Join our backend team to build scalable APIs and microservices. Work with Python, FastAPI, and cloud technologies.",
            required_skills=["Python", "FastAPI", "PostgreSQL", "Kubernetes", "REST APIs"],
            location="Remote",
            job_type="Full-time",
            experience_required=4,
            salary_min=120000,
            salary_max=160000,
            is_active=True
        )
        db.add(job2)
        db.flush()
    
    job3 = db.query(Job).filter(Job.title == "Frontend Developer").first()
    if not job3:
        job3 = Job(
            title="Frontend Developer",
            company="Tech Innovations Inc.",
            description="Build beautiful and responsive user interfaces. Work with React, TypeScript, and modern CSS frameworks.",
            required_skills=["React", "JavaScript", "CSS", "HTML", "TypeScript"],
            location="San Francisco, CA",
            job_type="Full-time",
            experience_required=3,
            salary_min=110000,
            salary_max=150000,
            is_active=True
        )
        db.add(job3)
        db.flush()
    
    db.commit()
    print("✓ Jobs created successfully!")
    
    # Create sample matches
    try:
        # Match candidate1 with job1
        match1 = db.query(Match).filter(
            Match.candidate_id == candidate1.id,
            Match.job_id == job1.id
        ).first()
        if not match1:
            match1 = Match(
                candidate_id=candidate1.id,
                job_id=job1.id,
                semantic_similarity=0.92,
                skill_overlap_score=0.88,
                experience_alignment=0.85,
                overall_score=0.88,
                match_explanation="Strong match! Alice has extensive full stack experience with Python, JavaScript, React, and FastAPI. Her experience level and skills closely match the Senior Full Stack Developer position."
            )
            db.add(match1)
        
        # Match candidate2 with job2
        match2 = db.query(Match).filter(
            Match.candidate_id == candidate2.id,
            Match.job_id == job2.id
        ).first()
        if not match2:
            match2 = Match(
                candidate_id=candidate2.id,
                job_id=job2.id,
                semantic_similarity=0.95,
                skill_overlap_score=0.92,
                experience_alignment=0.89,
                overall_score=0.92,
                match_explanation="Excellent match! Bob's expertise in Python, FastAPI, PostgreSQL, and Kubernetes aligns perfectly with the Backend Engineer role. His 8 years of experience exceeds the mid-level requirement."
            )
            db.add(match2)
        
        # Match candidate1 with job2
        match3 = db.query(Match).filter(
            Match.candidate_id == candidate1.id,
            Match.job_id == job2.id
        ).first()
        if not match3:
            match3 = Match(
                candidate_id=candidate1.id,
                job_id=job2.id,
                semantic_similarity=0.87,
                skill_overlap_score=0.83,
                experience_alignment=0.82,
                overall_score=0.84,
                match_explanation="Good match! Alice's full stack background includes the required Python and FastAPI skills. She has some experience with Kubernetes and can quickly learn any missing areas."
            )
            db.add(match3)
        
        # Match candidate1 with job3
        match4 = db.query(Match).filter(
            Match.candidate_id == candidate1.id,
            Match.job_id == job3.id
        ).first()
        if not match4:
            match4 = Match(
                candidate_id=candidate1.id,
                job_id=job3.id,
                semantic_similarity=0.89,
                skill_overlap_score=0.91,
                experience_alignment=0.88,
                overall_score=0.89,
                match_explanation="Strong match! Alice's React and JavaScript skills make her a great fit for the Frontend Developer role. She can handle both frontend and backend aspects."
            )
            db.add(match4)
        
        # Match candidate3 with job3
        match5 = db.query(Match).filter(
            Match.candidate_id == candidate3.id,
            Match.job_id == job3.id
        ).first()
        if not match5:
            match5 = Match(
                candidate_id=candidate3.id,
                job_id=job3.id,
                semantic_similarity=0.85,
                skill_overlap_score=0.87,
                experience_alignment=0.80,
                overall_score=0.84,
                match_explanation="Good match! Sarah's React and CSS skills match the Frontend Developer position. Her design background provides an additional advantage for creating beautiful UIs."
            )
            db.add(match5)
        
        db.commit()
        print("✓ Matches created successfully!")
    except Exception as e:
        print(f"Note: Matches may already exist - {str(e)}")
        db.rollback()
    
    print("\n" + "=" * 60)
    print("TEST DATA CREATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nTest Accounts:")
    print(f"  Recruiter: recruiter@example.com / Recruiter@1234")
    print(f"  Candidate 1: jobseeker@example.com / Jobseeker@1234")
    print(f"  Candidate 2: bob.engineer@example.com / Bob@1234")
    print(f"  Candidate 3: sarah.designer@example.com / Sarah@1234")
    print("\nJobs Created:")
    print(f"  Job 1: Senior Full Stack Developer (ID: {job1.id})")
    print(f"  Job 2: Backend Engineer (ID: {job2.id})")
    print(f"  Job 3: Frontend Developer (ID: {job3.id})")
    print("\nMatches Created:")
    print(f"  Candidate 1 with Job 1 (88% match)")
    print(f"  Candidate 2 with Job 2 (92% match)")
    print(f"  Candidate 1 with Job 2 (84% match)")
    print(f"  Candidate 1 with Job 3 (89% match)")
    print(f"  Candidate 3 with Job 3 (84% match)")
    print("\nHow to Test:")
    print("  1. Start backend: python run_server.py")
    print("  2. Start frontend: npm run dev")
    print("  3. Login as recruiter@example.com / Recruiter@1234")
    print("  4. Navigate to Matches tab")
    print("  5. Select one of the jobs from the dropdown")
    print("  6. View matching candidates with scores!")
    print("=" * 60)

except Exception as e:
    print(f"✗ Error creating test data: {str(e)}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
