
from app.core.config import settings
import sys

def check_config():
    print("--- Detailed Configuration Check ---")
    
    # Check Email Config
    print("\n[ EMAIL ]")
    print(f"  MAIL_USERNAME: {'✅ OK' if settings.MAIL_USERNAME else '❌ MISSING'}")
    print(f"  MAIL_PASSWORD: {'✅ OK' if settings.MAIL_PASSWORD else '❌ MISSING'}")
    print(f"  MAIL_FROM:     {settings.MAIL_FROM}")
    print(f"  MAIL_SERVER:   {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
    
    # Check SMS Config
    print("\n[ SMS ]")
    print(f"  TWILIO_ACCOUNT_SID:  { '✅ OK' if settings.TWILIO_ACCOUNT_SID else '❌ MISSING'}")
    print(f"  TWILIO_AUTH_TOKEN:   { '✅ OK' if settings.TWILIO_AUTH_TOKEN else '❌ MISSING'}")
    print(f"  TWILIO_PHONE_NUMBER: { '✅ OK' if settings.TWILIO_PHONE_NUMBER else '❌ MISSING (Required for SMS)'}")
        
    print("\n--- Summary ---")
    email_ok = bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD)
    sms_ok = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER)
    
    if email_ok:
        print("✅ Email notifications are ACTIVE.")
    else:
        print("❌ Email notifications are DISABLED (Missing credentials).")
        
    if sms_ok:
        print("✅ SMS notifications are ACTIVE.")
    else:
        print("⚠️ SMS notifications are DISABLED (Missing phone number or credentials).")

if __name__ == "__main__":
    check_config()
