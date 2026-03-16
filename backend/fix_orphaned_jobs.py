from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_orphaned_jobs():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # Get the first recruiter
        recruiter = conn.execute(text("SELECT id FROM users WHERE role = 'recruiter' LIMIT 1")).fetchone()
        
        if not recruiter:
            print("❌ No recruiter found in the database. Please create a recruiter account first.")
            return
            
        recruiter_id = recruiter[0]
        print(f"Found recruiter: {recruiter_id}")
        
        # Update jobs with null recruiter_id
        result = conn.execute(
            text("UPDATE jobs SET recruiter_id = :rid WHERE recruiter_id IS NULL"),
            {"rid": recruiter_id}
        )
        conn.commit()
        print(f"✅ Successfully associated {result.rowcount} orphaned jobs with recruiter {recruiter_id}.")

if __name__ == "__main__":
    fix_orphaned_jobs()
