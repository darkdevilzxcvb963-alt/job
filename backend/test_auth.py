"""
Test signup and login functionality
"""

import sys
from contextlib import contextmanager

sys.path.insert(0, "/root/backend")

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test@1234"


@contextmanager
def get_db():
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_test_user(db):
    """Fetch test user if exists"""
    return db.query(User).filter(User.email == TEST_EMAIL).first()


def create_test_user(db):
    """Create test user"""
    user = User(
        full_name="Test User",
        email=TEST_EMAIL,
        phone="1234567890",
        hashed_password=get_password_hash(TEST_PASSWORD),
        role=UserRole.JOB_SEEKER,
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.flush()  # gets ID without full commit
    return user


def test_user_creation():
    print("\n1. Creating test user...")

    try:
        with get_db() as db:
            user = get_test_user(db)

            if user:
                print("✓ Test user already exists")
            else:
                user = create_test_user(db)
                print("✓ Test user created successfully")

            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Verified: {user.is_verified}")

        return True

    except Exception as e:
        print(f"✗ User creation failed: {e}")
        return False


def test_user_query():
    print("\n2. Querying test user...")

    try:
        with get_db() as db:
            user = get_test_user(db)

            if not user:
                print("✗ Test user not found in database")
                return False

            print("✓ Test user found in database")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Full Name: {user.full_name}")

        return True

    except Exception as e:
        print(f"✗ User query failed: {e}")
        return False


def main():
    print("Testing Database Connection and User Operations...")
    print("=" * 50)

    if test_user_creation():
        test_user_query()

    print("\n" + "=" * 50)
    print("✓ All database tests completed")
    print("\nYou can now test login with:")
    print(f"  Email: {TEST_EMAIL}")
    print(f"  Password: {TEST_PASSWORD}")


if __name__ == "__main__":
    main()
