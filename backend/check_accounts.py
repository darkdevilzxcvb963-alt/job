from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()

print("\n" + "="*60)
print("CURRENT USER ACCOUNTS IN DATABASE")
print("="*60)

if not users:
    print("\n⚠️  NO USERS FOUND IN DATABASE!")
else:
    for u in users:
        print(f"\n{u.role}:")
        print(f"  Email: {u.email}")
        print(f"  Name: {u.full_name}")
        print(f"  Active: {u.is_active}")
        print(f"  Verified: {u.is_verified}")

print("\n" + "="*60)
db.close()
