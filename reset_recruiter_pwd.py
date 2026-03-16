
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_pwd():
    db = SessionLocal()
    try:
        email = "recruiterhiring56@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        if user:
            new_pwd = "Matched2024!"
            user.hashed_password = get_password_hash(new_pwd)
            db.commit()
            print(f"Password reset success for {email}")
        else:
            print(f"User {email} not found")
    finally:
        db.close()

if __name__ == "__main__":
    reset_pwd()
