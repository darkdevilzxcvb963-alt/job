import sys
import os
sys.path.append(os.getcwd())

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash

def reset_password():
    print("Resetting admin password...")
    try:
        db = next(get_db())
        admin_email = "admin@example.com"
        user = db.query(User).filter(User.email == admin_email).first()
        
        if user:
            new_password = "Admin@1234"
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            print(f"✅ Admin password reset to: {new_password}")
        else:
            print(f"❌ Admin user NOT found: {admin_email}")
            
    except Exception as e:
        print(f"❌ Error resetting password: {e}")

if __name__ == "__main__":
    reset_password()
