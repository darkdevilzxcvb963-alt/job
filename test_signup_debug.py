#!/usr/bin/env python
"""Debug signup endpoint errors"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, Base, engine  # type: ignore
from app.models.user import User, UserRole  # type: ignore
from app.core.security import get_password_hash  # type: ignore
from datetime import datetime, timedelta
from sqlalchemy import text

# Create all tables first
Base.metadata.create_all(bind=engine)
print("✓ Database tables created")

# Test database connection
db = SessionLocal()
try:
    # Check if users table exists and is accessible
    result = db.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users'"))
    table_exists = result.scalar() > 0
    print(f"✓ Users table exists: {table_exists}")
    
    # Try creating a user directly
    verification_token = "test_token_12345"
    hashed_password = get_password_hash("TestPass123")
    
    new_user = User(
        full_name="Test User Direct",
        email="direct_test@test.com",
        phone="1234567890",
        hashed_password=hashed_password,
        role=UserRole.JOB_SEEKER,
        verification_token=verification_token,
        verification_token_expires=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"✓ User created successfully with ID: {new_user.id}")
    
except Exception as e:
    import traceback
    print(f"✗ Error: {type(e).__name__}: {e}")
    traceback.print_exc()
finally:
    db.close()
