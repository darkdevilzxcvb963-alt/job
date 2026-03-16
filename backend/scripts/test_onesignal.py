
import asyncio
import os
import sys

# Ensure PYTHONPATH includes current directory
sys.path.append(os.getcwd())

from app.services.notification_service import NotificationService
from app.core.config import settings

async def test_onesignal():
    print("--- OneSignal Integration Diagnostic ---")
    print(f"App ID: {settings.ONESIGNAL_APP_ID or 'MISSING'}")
    print(f"API Key: {'PRESENT' if settings.ONESIGNAL_REST_API_KEY else 'MISSING'}")
    
    ns = NotificationService()
    
    test_email = "appleballcatdog54321@gmail.com"
    test_phone = "+917418735076" # From existing config
    
    print(f"\n1. Testing Push Notification...")
    # Using a fake user ID for testing
    push_success = await ns.send_push_notification("test-user-123", "Test Title", "This is a test push notification from Python.")
    print(f"Push Result: {'SUCCESS' if push_success else 'FAILED (See logs)'}")
    
    print(f"\n2. Testing Email via OneSignal...")
    email_success = await ns.send_email(test_email, "OneSignal Test Email", "<h1>Testing OneSignal</h1><p>Sent via unified NotificationService.</p>")
    print(f"Email Result: {'SUCCESS' if email_success else 'FAILED (Check fallback logs)'}")

    print(f"\n3. Testing SMS via OneSignal...")
    sms_success = await ns.send_sms(test_phone, "OneSignal SMS Test")
    print(f"SMS Result: {'SUCCESS' if sms_success else 'FAILED (Check fallback logs)'}")

if __name__ == "__main__":
    asyncio.run(test_onesignal())
