import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.core.database import Base
from sqlalchemy import create_engine
from app.models.user import User, CandidateProfile, RecruiterProfile
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.models.password_reset import PasswordReset
from app.models.user_session import UserSession

test_db = "sqlite:///test_init.db"
engine = create_engine(test_db)

print(f"Creating tables in {test_db}...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    import sqlite3
    conn = sqlite3.connect("test_init.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables in test_init.db: {tables}")
    
    if "recruiter_profiles" in tables:
        print("✓ recruiter_profiles is present.")
    else:
        print("✗ recruiter_profiles is MISSING!")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    if os.path.exists("test_init.db"):
        os.remove("test_init.db")
