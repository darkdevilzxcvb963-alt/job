"""
Database migration script — creates all tables using SQLAlchemy models.
Safe to run multiple times (SQLAlchemy skips existing tables).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, engine

# Import all models so SQLAlchemy registers them
from app.models.user import User, CandidateProfile, RecruiterProfile
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.models.password_reset import PasswordReset
from app.models.user_session import UserSession
from app.models.application import Application
from app.models.notification import Notification

print("Creating / verifying database tables...")
Base.metadata.create_all(bind=engine)
print("Done! Tables created/verified:")
for tbl in Base.metadata.sorted_tables:
    print(f"   - {tbl.name}")
