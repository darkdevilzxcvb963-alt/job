import sys
import os
import json
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def setup_account():
    db = SessionLocal()
    try:
        email = "srihariharan26ias@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        
        password = "Password@123"
        hashed = get_password_hash(password)
        
        if user:
            user.hashed_password = hashed
            print(f"[OK] Reset password for existing user {email}")
        else:
            user = User(
                full_name="Sri Hariharan",
                email=email,
                hashed_password=hashed,
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            print(f"[OK] Created new user {email}")
        
        db.commit()
        print(f"Login Email: {email}")
        print(f"Login Password: {password}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_account()
