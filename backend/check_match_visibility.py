from sqlalchemy import create_engine, text
from app.core.config import settings

def check_match_visibility():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("\n--- Recruiter ID Map ---")
        recruiters = conn.execute(text("SELECT id, email FROM users WHERE role = 'recruiter'")).fetchall()
        for r in recruiters:
            print(f"Recruiter: {r.email} | ID: {r.id}")

        print("\n--- Jobs Ownership ---")
        jobs = conn.execute(text("SELECT id, title, recruiter_id FROM jobs")).fetchall()
        for job in jobs:
            print(f"Job: {job.title} | Owned by: {job.recruiter_id}")

        print("\n--- Matches Distribution ---")
        matches = conn.execute(text("SELECT m.id, m.job_id, j.recruiter_id FROM matches m JOIN jobs j ON m.job_id = j.id")).fetchall()
        for m in matches:
            print(f"Match: {m.id} | Job: {m.job_id} | Recruiter: {m.recruiter_id}")

if __name__ == "__main__":
    check_match_visibility()
