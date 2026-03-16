#!/usr/bin/env python
"""
Create or update admin account with correct credentials
"""
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

try:
    print("\n" + "="*60)
    print("CREATING/UPDATING ADMIN ACCOUNT")
    print("="*60)
    
    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    
    if admin:
        print("\n✓ Admin account found - updating password...")
        admin.hashed_password = get_password_hash("Admin@1234")
        admin.is_active = True
        admin.is_verified = True
        admin.role = UserRole.ADMIN
        db.commit()
        print("✅ Admin password updated successfully!")
    else:
        print("\n✓ Creating new admin account...")
        admin = User(
            full_name="Admin User",
            email="admin@example.com",
            phone="5550000000",
            hashed_password=get_password_hash("Admin@1234"),
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=True,
            bio="Platform Administrator",
            location="System"
        )
        db.add(admin)
        db.commit()
        print("✅ Admin account created successfully!")
    
    print("\n" + "="*60)
    print("ADMIN CREDENTIALS")
    print("="*60)
    print(f"Email:    admin@example.com")
    print(f"Password: Admin@1234")
    print(f"Role:     {admin.role}")
    print("="*60)
    print("\n✅ You can now log in at: http://localhost:3000/login")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
