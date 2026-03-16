
import sys
import os
from pathlib import Path

# Add the current directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.core.security import create_access_token, verify_token
from app.core.config import settings

def run_diagnostic():
    print("=== AUTH DIAGNOSTIC ===")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print(f"SECRET_KEY: {settings.SECRET_KEY[:5]}...")
    
    db = SessionLocal()
    try:
        # 1. Check users in DB
        users = db.query(User).all()
        print(f"Total users in DB: {len(users)}")
        for u in users:
            print(f"  - {u.email} (Role: {u.role}, ID: {u.id}, Type: {type(u.id)})")
            
        if not users:
            print("ERROR: No users found in DB. Run seed scripts.")
            return

        # 2. Test Token Generation and Verification for the first user
        test_user = users[0]
        role_value = test_user.role.value if hasattr(test_user.role, "value") else test_user.role
        token = create_access_token(data={"sub": test_user.id, "role": role_value})
        print(f"\nGenerated token for {test_user.email}")
        
        try:
            payload = verify_token(token, "access")
            print(f"Verification success: {payload}")
            
            sub = payload.get("sub")
            print(f"Sub in payload: {sub} (Type: {type(sub)})")
            
            # 3. Test DB Lookup with Sub
            found_user = db.query(User).filter(User.id == sub).first()
            if found_user:
                print(f"User lookup success: {found_user.email}")
            else:
                print(f"ERROR: User lookup failed for ID {sub}")
                
        except Exception as e:
            print(f"Verification failed: {e}")
            
    finally:
        db.close()

if __name__ == "__main__":
    run_diagnostic()
