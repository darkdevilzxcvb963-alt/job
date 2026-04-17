import sys
import os
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User

def check_all_hashes():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Total users: {len(users)}")
    for user in users:
        hp = user.hashed_password
        status = "Bcrypt" if hp.startswith('$2b$') or hp.startswith('$2a$') else f"UNKNOWN ({hp[:5]}...)"
        print(f"User: {user.email} | Hash Format: {status} | Length: {len(hp)}")
    db.close()

if __name__ == "__main__":
    check_all_hashes()
