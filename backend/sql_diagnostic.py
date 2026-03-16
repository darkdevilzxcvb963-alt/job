"""
SQL-based diagnostic
"""
import sqlite3
import json
import os

# Database is in parent directory
db_path = os.path.join(os.path.dirname(__file__), "..", "resume_matching.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*60)
print("DATABASE DIAGNOSTIC")
print("="*60)

# Count users
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM users WHERE role='job_seeker'")
job_seekers = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM users WHERE role='recruiter'")
recruiters = cursor.fetchone()[0]

print(f"\nUSERS: {total_users} total ({job_seekers} job seekers, {recruiters} recruiters)")

# Count jobs
cursor.execute("SELECT COUNT(*) FROM jobs")
total_jobs = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active=1")
active_jobs = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_embedding IS NOT NULL")
jobs_with_emb = cursor.fetchone()[0]

print(f"JOBS: {total_jobs} total ({active_jobs} active, {jobs_with_emb} with embeddings)")

# Count candidates
cursor.execute("SELECT COUNT(*) FROM candidates")
total_candidates = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM candidates WHERE resume_embedding IS NOT NULL")
candidates_with_emb = cursor.fetchone()[0]

print(f"CANDIDATES: {total_candidates} total ({candidates_with_emb} with embeddings)")

# Count matches
cursor.execute("SELECT COUNT(*) FROM matches")
total_matches = cursor.fetchone()[0]

print(f"MATCHES: {total_matches} total")

print("\n" + "="*60)
print("ROOT CAUSE ANALYSIS")
print("="*60)

if total_users == 0:
    print("\n❌ ISSUE: No users in database")
    print("   ACTION: Sign up as both job seeker and recruiter")
elif job_seekers == 0:
    print("\n❌ ISSUE: No job seekers registered")
    print("   ACTION: Sign up as a job seeker")
elif recruiters == 0:
    print("\n❌ ISSUE: No recruiters registered")
    print("   ACTION: Sign up as a recruiter")
else:
    print(f"\n✅ Users exist: {job_seekers} job seekers, {recruiters} recruiters")

if total_jobs == 0:
    print("\n❌ ISSUE: No jobs posted")
    print("   ACTION: Recruiter needs to post a job")
elif active_jobs == 0:
    print("\n❌ ISSUE: No active jobs")
    print("   ACTION: Activate existing jobs or post new ones")
elif jobs_with_emb == 0:
    print("\n❌ ISSUE: Jobs exist but have no embeddings")
    print("   ACTION: Jobs were not processed correctly during creation")
else:
    print(f"\n✅ Jobs ready: {active_jobs} active jobs with embeddings")

if total_candidates == 0:
    print("\n❌ ISSUE: No candidate profiles")
    print("   ACTION: Job seeker needs to upload a resume")
elif candidates_with_emb == 0:
    print("\n❌ ISSUE: Candidates exist but have no embeddings")
    print("   ACTION: Resumes were not processed correctly")
else:
    print(f"\n✅ Candidates ready: {candidates_with_emb} with processed resumes")

if total_matches == 0:
    if active_jobs > 0 and candidates_with_emb > 0:
        print("\n❌ CRITICAL ISSUE: Jobs and candidates exist but NO MATCHES!")
        print("   POSSIBLE CAUSES:")
        print("   1. Match generation logic never ran")
        print("   2. Match threshold too high (scores below 0.1)")
        print("   3. Error during match generation (check logs)")
        print("   ACTION: Manually trigger match generation")
    else:
        print("\n⚠️  No matches (expected - missing jobs or candidates)")
else:
    print(f"\n✅ Matches exist: {total_matches} matches generated")

print("\n" + "="*60)

conn.close()
