import sys
import os
sys.path.append(os.getcwd())

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash

def set_admin_password():
    print("Allocating password for admin...")
    try:
        db = next(get_db())
        admin_email = "admin@example.com"
        user = db.query(User).filter(User.email == admin_email).first()
        
        if user:
            new_password = "Admin@1234"
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            print(f"✅ Admin password successfully set to: {new_password}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
        else:
            print(f"❌ Admin user NOT found: {admin_email}")
            # Optional: Create if not exists?
            # For now, just report not found as per previous context it should exist
            
    except Exception as e:
        print(f"❌ Error setting password: {e}")

if __name__ == "__main__":
    set_admin_password()
