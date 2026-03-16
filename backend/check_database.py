"""
Diagnostic script to check database status
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

db = SessionLocal()

print("=" * 60)
print("DATABASE STATUS CHECK")
print("=" * 60)

# Count jobs
total_jobs = db.query(Job).count()
active_jobs = db.query(Job).filter(Job.is_active == True).count()
print(f"\n📋 Jobs:")
print(f"   Total: {total_jobs}")
print(f"   Active: {active_jobs}")

# Count candidates
total_candidates = db.query(Candidate).count()
candidates_with_embeddings = db.query(Candidate).filter(Candidate.resume_embedding != None).count()
print(f"\n👤 Candidates:")
print(f"   Total: {total_candidates}")
print(f"   With embeddings: {candidates_with_embeddings}")

# Count matches
total_matches = db.query(Match).count()
print(f"\n🔗 Matches:")
print(f"   Total: {total_matches}")

# Show some sample data
if active_jobs > 0:
    print(f"\n📌 Sample Active Jobs:")
    for job in db.query(Job).filter(Job.is_active == True).limit(3).all():
        has_embedding = "✅" if job.job_embedding else "❌"
        print(f"   {has_embedding} {job.title} at {job.company}")

if total_candidates > 0:
    print(f"\n📌 Sample Candidates:")
    for candidate in db.query(Candidate).limit(3).all():
        has_embedding = "✅" if candidate.resume_embedding else "❌"
        skills_count = len(candidate.skills) if candidate.skills else 0
        print(f"   {has_embedding} {candidate.name} ({skills_count} skills)")

if total_matches > 0:
    print(f"\n📌 Sample Matches:")
    for match in db.query(Match).limit(3).all():
        print(f"   Score: {match.overall_score:.2%}")

print("\n" + "=" * 60)

# Diagnosis
print("\nDIAGNOSIS:")
if active_jobs == 0:
    print("⚠️  NO ACTIVE JOBS - Matches cannot be generated without jobs!")
elif candidates_with_embeddings == 0:
    print("⚠️  NO CANDIDATES WITH EMBEDDINGS - Upload and process resume first!")
elif total_matches == 0:
    print("⚠️  NO MATCHES EXIST - Click 'Re-evaluate Matches' or check threshold!")
else:
    print("✅ System looks healthy - matches should be visible!")

db.close()
