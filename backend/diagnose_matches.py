"""
Simple diagnostic script to check matching status
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.user import User

db = SessionLocal()

print("\n" + "="*60)
print("MATCHING DIAGNOSTIC REPORT")
print("="*60)

# Check Users
total_users = db.query(User).count()
job_seekers = db.query(User).filter(User.role == "job_seeker").count()
recruiters = db.query(User).filter(User.role == "recruiter").count()

print(f"\n1. USERS:")
print(f"   Total users: {total_users}")
print(f"   Job seekers: {job_seekers}")
print(f"   Recruiters: {recruiters}")

# Check Jobs
total_jobs = db.query(Job).count()
active_jobs = db.query(Job).filter(Job.is_active == True).count()
jobs_with_embeddings = db.query(Job).filter(Job.job_embedding != None).count()

print(f"\n2. JOBS:")
print(f"   Total jobs: {total_jobs}")
print(f"   Active jobs: {active_jobs}")
print(f"   Jobs with embeddings: {jobs_with_embeddings}")

if active_jobs > 0:
    print(f"\n   Sample jobs:")
    for job in db.query(Job).filter(Job.is_active == True).limit(3).all():
        emb_status = "YES" if job.job_embedding else "NO"
        print(f"   - {job.title} at {job.company} (Embedding: {emb_status})")

# Check Candidates
total_candidates = db.query(Candidate).count()
candidates_with_embeddings = db.query(Candidate).filter(Candidate.resume_embedding != None).count()

print(f"\n3. CANDIDATES:")
print(f"   Total candidates: {total_candidates}")
print(f"   Candidates with embeddings: {candidates_with_embeddings}")

if total_candidates > 0:
    print(f"\n   Sample candidates:")
    for candidate in db.query(Candidate).limit(3).all():
        emb_status = "YES" if candidate.resume_embedding else "NO"
        skills_count = 0
        if candidate.skills:
            if isinstance(candidate.skills, dict):
                skills_count = sum(len(v) for v in candidate.skills.values() if isinstance(v, list))
            elif isinstance(candidate.skills, list):
                skills_count = len(candidate.skills)
        print(f"   - {candidate.name} ({candidate.email}) - Skills: {skills_count}, Embedding: {emb_status}")

# Check Matches
total_matches = db.query(Match).count()

print(f"\n4. MATCHES:")
print(f"   Total matches: {total_matches}")

if total_matches > 0:
    print(f"\n   Sample matches:")
    for match in db.query(Match).limit(5).all():
        candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
        job = db.query(Job).filter(Job.id == match.job_id).first()
        if candidate and job:
            print(f"   - {candidate.name} <-> {job.title} (Score: {match.overall_score:.2%})")

print("\n" + "="*60)
print("DIAGNOSIS:")
print("="*60)

issues = []

if total_users == 0:
    issues.append("❌ NO USERS - Sign up first!")
elif job_seekers == 0:
    issues.append("❌ NO JOB SEEKERS - Sign up as a job seeker!")

if total_jobs == 0:
    issues.append("❌ NO JOBS - Post a job first!")
elif active_jobs == 0:
    issues.append("❌ NO ACTIVE JOBS - All jobs are inactive!")
elif jobs_with_embeddings == 0:
    issues.append("❌ JOBS MISSING EMBEDDINGS - Jobs were not processed correctly!")

if total_candidates == 0:
    issues.append("❌ NO CANDIDATES - Upload a resume first!")
elif candidates_with_embeddings == 0:
    issues.append("❌ CANDIDATES MISSING EMBEDDINGS - Resumes were not processed!")

if total_matches == 0 and active_jobs > 0 and candidates_with_embeddings > 0:
    issues.append("❌ NO MATCHES GENERATED - Matching logic may have failed!")

if issues:
    for issue in issues:
        print(f"\n{issue}")
else:
    print("\n✅ All systems operational! Matches should be visible.")

print("\n" + "="*60)

db.close()
