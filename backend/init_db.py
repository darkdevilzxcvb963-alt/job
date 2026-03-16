#!/usr/bin/env python
"""
Initialize database with tables
"""
import sys
from app.core.database import Base, engine

# Import all models to register them
from app.models.user import User
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.models.password_reset import PasswordReset
from app.models.user_session import UserSession

def init_db():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating database tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
