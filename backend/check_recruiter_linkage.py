from sqlalchemy import create_engine, text
from app.core.config import settings

def check_recruiter_linkage():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("\n--- Checking Jobs ---")
        jobs = conn.execute(text("SELECT id, title, recruiter_id FROM jobs")).fetchall()
        for job in jobs:
            print(f"ID: {job.id} | Title: {job.title} | RecruiterID: {job.recruiter_id}")

        print("\n--- Checking Matches ---")
        matches = conn.execute(text("SELECT id, job_id, candidate_id FROM matches")).fetchall()
        print(f"Total Matches: {len(matches)}")
        
        print("\n--- Checking Users (Recruiters) ---")
        recruiters = conn.execute(text("SELECT id, email, role FROM users WHERE role = 'recruiter'")).fetchall()
        for r in recruiters:
            print(f"ID: {r.id} | Email: {r.email}")

if __name__ == "__main__":
    check_recruiter_linkage()
