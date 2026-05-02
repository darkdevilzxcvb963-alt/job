
import asyncio
import os
import sys

# Ensure PYTHONPATH includes current directory
sys.path.append(os.getcwd())

from app.services.notification_service import NotificationService
from app.core.config import settings

async def test_notifications():
    print("--- Notification System Diagnostic ---")
    print(f"OneSignal App ID: {settings.ONESIGNAL_APP_ID or 'MISSING'}")
    print(f"Resend API Key: {'PRESENT' if settings.RESEND_API_KEY else 'MISSING'}")
    print(f"SMTP Username: {settings.MAIL_USERNAME or 'MISSING'}")
    
    ns = NotificationService()
    
    test_email = "appleballcatdog54321@gmail.com"
    
    print(f"\n1. Testing Email Delivery Flow...")
    print("This will try OneSignal -> Resend -> SMTP in order.")
    email_success = await ns.send_email(test_email, "Notification Test Email", "<h1>Testing Notifications</h1><p>Sent via updated NotificationService with Resend support.</p>")
    print(f"Result: {'SUCCESS' if email_success else 'FAILED'}")

    if settings.RESEND_API_KEY:
        print(f"\n2. Testing Resend Directly...")
        resend_success = await ns._send_resend_email(test_email, "Resend Direct Test", "<h1>Resend is working!</h1>")
        print(f"Resend Direct Result: {'SUCCESS' if resend_success else 'FAILED'}")

if __name__ == "__main__":
    asyncio.run(test_notifications())
