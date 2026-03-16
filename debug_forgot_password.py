import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent / 'backend'))

from app.core.database import SessionLocal
from app.models.user import User
from app.api.v1.auth import forgot_password
from app.schemas.auth import PasswordResetRequest
import asyncio

async def debug_forgot_password(email_to_test):
    print(f"DEBUG: Testing forgot_password for email: '{email_to_test}'")
    db = SessionLocal()
    try:
        # 1. Check what the DB says for this email
        user = db.query(User).filter(User.email == email_to_test.lower().strip()).first()
        if user:
            print(f"DEBUG: Found user in DB:")
            print(f"  ID: {user.id}")
            print(f"  Email: '{user.email}'")
            print(f"  Full Name: {user.full_name}")
        else:
            print(f"DEBUG: No user found in DB for '{email_to_test}'")
            # List all users to see if something similar exists
            all_users = db.query(User.email).all()
            print(f"DEBUG: All emails in DB: {[u[0] for u in all_users]}")
            
        # 2. Simulate the API call logic (roughly)
        # Note: We can't easily await the actual endpoint because of Depends/etc.
        # but we can see what it would do.
        
    finally:
        db.close()

if __name__ == "__main__":
    test_email = sys.argv[1] if len(sys.argv) > 1 else 'apitest@example.com'
    asyncio.run(debug_forgot_password(test_email))
