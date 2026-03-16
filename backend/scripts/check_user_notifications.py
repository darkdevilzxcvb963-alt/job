
import asyncio
import traceback
import sys
import os
from app.core.database import SessionLocal
from app.models.user import User
from app.services.notification_service import NotificationService
from app.core.email import send_verification_email
from app.core.config import settings
from loguru import logger

async def check_user_and_test_email(email):
    log_file = "diag_results.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"--- Checking User: {email} ---\n")
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                f.write(f"ERROR: User with email {email} NOT FOUND in database.\n")
                return
            
            f.write(f"SUCCESS: User found: ID={user.id}, Name={user.full_name}, Verified={user.is_verified}\n")
            
            f.write("\n--- Testing Email Notification Service ---\n")
            try:
                ns = NotificationService()
                success = ns.send_email(
                    to_email=email,
                    subject="Test Notification Service",
                    html_body="<h1>This is a test notification</h1><p>If you see this, the NotificationService is working.</p>"
                )
                f.write(f"NotificationService test: {'SUCCESS' if success else 'FAILED'}\n")
            except Exception as e:
                f.write(f"ERROR: NotificationService FAILED with error: {e}\n")
                f.write(traceback.format_exc())
            
            f.write("\n--- Testing Core Email (Verification) ---\n")
            try:
                # Core email uses FastMail (async)
                success_v = await send_verification_email(email, "test-token-123456", user.full_name)
                f.write(f"send_verification_email test: {'SUCCESS' if success_v else 'FAILED'}\n")
            except Exception as e:
                f.write(f"ERROR: send_verification_email FAILED with error: {e}\n")
                f.write(traceback.format_exc())
                
        except Exception as e:
            f.write(f"ERROR: Error during diagnostic: {e}\n")
            f.write(traceback.format_exc())
        finally:
            db.close()
    
    print(f"Diagnostic complete. Results written to {os.path.abspath(log_file)}")

if __name__ == "__main__":
    email = "appleballcatdog54321@gmail.com"
    asyncio.run(check_user_and_test_email(email))
