
from app.core.config import settings
import sys

def check_config():
    print("--- Detailed Configuration Check ---")
    
    # Check Email Config
    print("\n[ EMAIL ]")
    email_ok = bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD)
    sms_ok = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER)
    
    if email_ok:
        print("[OK] Email notifications are ACTIVE.")
    else:
        print("[FAIL] Email notifications are DISABLED (Missing credentials).")
        
    if sms_ok:
        print("[OK] SMS notifications are ACTIVE.")
    else:
        print("[WARN] SMS notifications are DISABLED (Missing phone number or credentials).")

if __name__ == "__main__":
    check_config()
