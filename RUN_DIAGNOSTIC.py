#!/usr/bin/env python
"""
Comprehensive Signup & Login Test
"""
import sys
import time
sys.path.insert(0, 'backend')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash, verify_password

def test_database():
    """Test database connection and user creation"""
    print("\n" + "="*60)
    print("TEST 1: Database Connection")
    print("="*60)
    
    db = SessionLocal()
    from sqlalchemy import text
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        print("Database connection successful")
        
        # Check if users table exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'users' in tables:
            print("Users table exists")
        else:
            print("Users table NOT found")
            return False
            
        return True
    except Exception as e:
        print(f"FAILED - Database error: {str(e)}")
        return False
    finally:
        db.close()

def test_user_creation():
    """Test creating a user"""
    print("\n" + "="*60)
    print("TEST 2: User Creation")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Clear test users
        test_email = "signup_test@example.com"
        existing = db.query(User).filter(User.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()
            print(f"Cleared existing test user")
        
        # Create new user
        new_user = User(
            full_name="Signup Test",
            email=test_email,
            phone="1234567890",
            hashed_password=get_password_hash("TestPass123"),
            role="job_seeker",
            is_verified=False,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"User created successfully")
        print(f"  - ID: {new_user.id}")
        print(f"  - Email: {new_user.email}")
        print(f"  - Role: {new_user.role}")
        
        return True
        
    except Exception as e:
        print(f"FAILED - User creation failed: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def test_password_verification():
    """Test password hashing and verification"""
    print("\n" + "="*60)
    print("TEST 3: Password Verification")
    print("="*60)
    
    try:
        password = "TestPass123"
        hashed = get_password_hash(password)
        
        is_valid = verify_password(password, hashed)
        if is_valid:
            print("Password verification works")
        else:
            print("FAILED - Password verification failed")
            return False
        
        # Test wrong password
        is_invalid = verify_password("WrongPass123", hashed)
        if not is_invalid:
            print("Wrong password rejected correctly")
        else:
            print("FAILED - Wrong password NOT rejected")
            return False
            
        return True
        
    except Exception as e:
        print(f"FAILED - Password test failed: {str(e)}")
        return False

def test_api_endpoint():
    """Test signup API endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Signup API Endpoint")
    print("="*60)
    
    try:
        import requests
        
        url = 'http://localhost:8000/api/v1/auth/signup'
        data = {
            'full_name': 'API Test User',
            'email': 'apitest@example.com',
            'phone': '9876543210',
            'password': 'ApiTest123',
            'role': 'recruiter'
        }
        
        print(f"POST {url}")
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 201:
            print(f"Signup successful (Status: {response.status_code})")
            user_data = response.json()
            print(f"  - Email: {user_data.get('email')}")
            print(f"  - Role: {user_data.get('role')}")
            return True
        elif response.status_code == 400:
            error = response.json().get('detail', 'Unknown error')
            if 'already exists' in error:
                print(f"Signup validation works (User exists)")
                return True
            else:
                print(f"FAILED - Signup failed: {error}")
                return False
        else:
            print(f"FAILED - Signup failed (Status: {response.status_code})")
            print(f"  Response: {response.json()}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("FAILED - Cannot connect to backend (http://127.0.0.1:8000)")
        print("  Make sure backend is running")
        return False
    except Exception as e:
        print(f"FAILED - API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  COMPREHENSIVE SIGNUP & LOGIN TEST")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Database", test_database()))
    time.sleep(0.5)
    results.append(("User Creation", test_user_creation()))
    time.sleep(0.5)
    results.append(("Password Verification", test_password_verification()))
    time.sleep(0.5)
    results.append(("API Endpoint", test_api_endpoint()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("="*60)
    if all_passed:
        print("\nALL TESTS PASSED - Signup system is working!\n")
        print("Frontend ready for signup at: http://localhost:3001/signup")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED - Check errors above\n")
        sys.exit(1)
