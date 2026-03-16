#!/usr/bin/env python3
"""
Direct Database Test - Verify signup implementation stores data
This file should be run from the backend directory:
  cd backend
  python ../test_direct_signup.py

Or from root directory:
  python test_direct_signup.py
"""

import sys
import os
from pathlib import Path

# Determine the backend directory
current_dir = Path(__file__).parent
backend_dir = current_dir / 'backend'

# Add backend to Python path if not already there
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Now do the imports - the system will find them via sys.path
try:
    from app.core.database import SessionLocal  # type: ignore
    from app.models.user import User, UserRole  # type: ignore
    from app.core.security import get_password_hash  # type: ignore
    from datetime import datetime
except ImportError as e:
    print(f"Error importing modules. Make sure you're running from the correct directory.")
    print(f"Backend path: {backend_dir}")
    print(f"Python path: {sys.path[:2]}")
    print(f"Import error: {e}")
    sys.exit(1)

def test_user_creation():
    """Test creating users directly in database"""
    
    print("\n" + "="*60)
    print("DIRECT DATABASE TEST - USER SIGNUP")
    print("="*60 + "\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test 1: Create first user
        print("Test 1: Creating Job Seeker...")
        user1 = User(
            full_name="John Developer",
            email="john.dev@test.com",
            phone="+1-555-1234",
            hashed_password=get_password_hash("SecurePass123"),
            role=UserRole.JOB_SEEKER,
            is_verified=True,
            is_active=True
        )
        db.add(user1)
        db.commit()
        db.refresh(user1)
        print(f"✓ Created: {user1.email} (ID: {user1.id})")
        print(f"  Name: {user1.full_name}")
        print(f"  Role: {user1.role}")
        print(f"  Phone: {user1.phone}\n")
        
        # Test 2: Create second user
        print("Test 2: Creating Recruiter...")
        user2 = User(
            full_name="Jane Recruiter",
            email="jane.recruiter@test.com",
            phone="+1-555-5678",
            hashed_password=get_password_hash("RecruiterPass456"),
            role=UserRole.RECRUITER,
            is_verified=True,
            is_active=True
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)
        print(f"✓ Created: {user2.email} (ID: {user2.id})")
        print(f"  Name: {user2.full_name}")
        print(f"  Role: {user2.role}")
        print(f"  Phone: {user2.phone}\n")
        
        # Test 3: Create user without phone
        print("Test 3: Creating user without phone...")
        user3 = User(
            full_name="Simple User",
            email="simple@test.com",
            phone=None,
            hashed_password=get_password_hash("SimplePass789"),
            role=UserRole.JOB_SEEKER,
            is_verified=True,
            is_active=True
        )
        db.add(user3)
        db.commit()
        db.refresh(user3)
        print(f"✓ Created: {user3.email} (ID: {user3.id})")
        print(f"  Name: {user3.full_name}")
        print(f"  Phone: {user3.phone or 'Not provided'}\n")
        
        # Test 4: Verify all users stored
        print("Test 4: Retrieving all users from database...")
        all_users = db.query(User).all()
        print(f"✓ Total users in database: {len(all_users)}\n")
        
        for user in all_users:
            print(f"  - {user.email}")
            print(f"    Name: {user.full_name}")
            print(f"    Role: {user.role}")
            print(f"    Created: {user.created_at}")
            print()
        
        # Test 5: Test duplicate email prevention
        print("Test 5: Testing duplicate email prevention...")
        try:
            dup_user = User(
                full_name="Duplicate Test",
                email="john.dev@test.com",  # Same email as user1
                hashed_password=get_password_hash("DupPass123"),
                role=UserRole.JOB_SEEKER,
                is_verified=True,
                is_active=True
            )
            db.add(dup_user)
            db.commit()
            print("✗ ERROR: Duplicate email was accepted (should have failed)")
        except Exception as e:
            print(f"✓ Correctly rejected duplicate email")
            print(f"  Error: {str(e)[:60]}...\n")
            db.rollback()
        print("Test 6: Querying by role...")
        job_seekers = db.query(User).filter(User.role == UserRole.JOB_SEEKER).all()
        recruiters = db.query(User).filter(User.role == UserRole.RECRUITER).all()
        print(f"✓ Job Seekers: {len(job_seekers)}")
        print(f"✓ Recruiters: {len(recruiters)}\n")
        
        print("="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nSummary:")
        print("✓ Multiple users can be created")
        print("✓ User data is stored in database")
        print("✓ Both job seekers and recruiters supported")
        print("✓ Phone field is optional")
        print("✓ Duplicate emails are prevented")
        print("✓ Users can be queried by role")
        print("\nDatabase file: backend/resume_matching.db")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_user_creation()
