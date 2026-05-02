
import asyncio
import os
import sys

# Ensure PYTHONPATH includes current directory
sys.path.append(os.getcwd())

from app.services.notification_service import NotificationService
from app.core.config import settings

async def test_notifications():
    print("--- Notification System Diagnostic ---")
    print(f"Mailjet API Key: {'PRESENT' if settings.MAILJET_API_KEY else 'MISSING'}")
    print(f"SMTP Username: {settings.MAIL_USERNAME or 'MISSING'}")
    
    ns = NotificationService()
    
    test_email = "kingofdarksp48@gmail.com"
    
    print(f"\n1. Testing Email Delivery Flow...")
    print("This will try Mailjet -> SMTP in order.")
    email_success = await ns.send_email(test_email, "Mailjet System Test", "<h1>Testing Mailjet</h1><p>Sent via updated NotificationService with Mailjet API.</p>")
    print(f"Result: {'SUCCESS' if email_success else 'FAILED'}")

    if settings.MAILJET_API_KEY:
        print(f"\n2. Testing Mailjet Directly...")
        mailjet_success = await ns._send_mailjet_email(test_email, "Mailjet Direct Test", "<h1>Mailjet API is working!</h1>")
        print(f"Mailjet Direct Result: {'SUCCESS' if mailjet_success else 'FAILED'}")

if __name__ == "__main__":
    asyncio.run(test_notifications())
