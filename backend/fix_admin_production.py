#!/usr/bin/env python
"""
Create or update admin account with correct credentials for Live/Production
"""
import sys
import os

# Add the current directory to sys.path to allow importing from 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def fix_admin():
    db = SessionLocal()
    try:
        print("\n" + "="*60)
        print("PRODUCTION ADMIN ACCOUNT SYNC")
        print("="*60)
        
        # Define Admin Credentials
        ADMIN_EMAIL = "admin@example.com"  # You can change this to your preferred admin email
        ADMIN_PASSWORD = "Admin@1234"      # You can change this to your preferred admin password
        
        # Check if admin exists
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        
        if admin:
            print(f"\n✓ Admin account found ({ADMIN_EMAIL}) - syncing status and password...")
            admin.hashed_password = get_password_hash(ADMIN_PASSWORD)
            admin.is_active = True
            admin.is_verified = True
            admin.role = UserRole.ADMIN
            admin.mfa_enabled = False  # Disable MFA to ensure you can get in
            db.commit()
            print("✅ Admin credentials synced successfully!")
        else:
            print(f"\n✓ Creating new admin account ({ADMIN_EMAIL})...")
            admin = User(
                full_name="Platform Admin",
                email=ADMIN_EMAIL,
                username="admin",
                phone="5550000000",
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_verified=True,
                is_active=True,
                mfa_enabled=False,
                bio="Platform Administrator",
                location="Production"
            )
            db.add(admin)
            db.commit()
            print("✅ Admin account created successfully!")
        
        print("\n" + "="*60)
        print("ADMIN CREDENTIALS FOR LOGIN")
        print("="*60)
        print(f"Email:    {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print(f"Role:     ADMIN")
        print("="*60)
        print("\n✅ You can now log in at your website's login page.")
        print("   If you still cannot log in, please check your database connection.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin()
