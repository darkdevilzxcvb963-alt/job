import sys
import os
sys.path.append(os.getcwd())

from app.core.database import get_db
from app.models.user import User

# This might be needed if running directly to ensure Enums are loaded
try:
    from app.models.user import UserRole
except ImportError:
    pass

def check_admin():
    print("Checking for admin user...")
    try:
        db = next(get_db())
        admin_email = "admin@example.com"
        user = db.query(User).filter(User.email == admin_email).first()
        
        if user:
            print(f"✅ Admin user found: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Verified: {user.is_verified}")
            # print(f"   Hashed Password: {user.hashed_password[:10]}...") 
        else:
            print(f"❌ Admin user NOT found: {admin_email}")
            
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin()
