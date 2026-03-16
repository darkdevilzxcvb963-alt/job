import sqlite3
import os
from pathlib import Path
import sys

# Add backend to path to get settings
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings

def migrate():
    db_url = settings.DATABASE_URL
    if "sqlite" not in db_url:
        print(f"Unsupported database for auto-migration: {db_url}")
        return

    db_path = db_url.replace("sqlite:///", "")
    print(f"Migrating database: {db_path}")

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "recruiter_id" not in columns:
            print("Adding recruiter_id column to jobs table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN recruiter_id VARCHAR(36)")
            conn.commit()
            print("✅ Successfully added recruiter_id column.")
        else:
            print("✅ recruiter_id column already exists.")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
