from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import verify_password

db = SessionLocal()

print("\n" + "="*60)
print("CHECKING ADMIN ACCOUNT")
print("="*60)

# Check if admin exists
admin = db.query(User).filter(User.email == "admin@example.com").first()

if not admin:
    print("\n❌ ADMIN ACCOUNT NOT FOUND!")
    print("\nThe admin account was not created during initialization.")
    print("You need to create it manually.")
else:
    print(f"\n✅ Admin account found!")
    print(f"   Email: {admin.email}")
    print(f"   Name: {admin.full_name}")
    print(f"   Role: {admin.role}")
    print(f"   Active: {admin.is_active}")
    print(f"   Verified: {admin.is_verified}")
    
    # Test password
    print("\n" + "-"*60)
    print("Testing password: Admin@1234")
    print("-"*60)
    
    if verify_password("Admin@1234", admin.hashed_password):
        print("✅ Password is CORRECT!")
    else:
        print("❌ Password is INCORRECT!")
        print("\nTrying other common passwords...")
        
        test_passwords = ["admin123", "Admin123", "admin@123", "Admin@123", "password"]
        for pwd in test_passwords:
            if verify_password(pwd, admin.hashed_password):
                print(f"✅ Found working password: {pwd}")
                break
        else:
            print("❌ None of the common passwords work.")
            print("The admin password needs to be reset.")

print("\n" + "="*60)
db.close()
