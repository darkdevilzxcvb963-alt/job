#!/usr/bin/env python
"""
Initialize database with all required tables
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.models.password_reset import PasswordReset
from app.models.user_session import UserSession

print("Initializing database...")
print("-" * 60)

try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
    
    # Verify tables exist
    db = SessionLocal()
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    db.close()
    
    print(f"\nCreated tables ({len(tables)}):")
    for table in sorted(tables):
        print(f"  ✓ {table}")
    
    print("-" * 60)
    print("✅ Database initialization complete!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
