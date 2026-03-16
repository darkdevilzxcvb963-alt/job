
import smtplib
from app.core.config import settings

def test_raw_smtp():
    print(f"--- Raw SMTP Test for {settings.MAIL_USERNAME} ---")
    print(f"Server: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
    try:
        server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
        server.set_debuglevel(1)
        server.ehlo()
        if settings.MAIL_TLS:
            server.starttls()
            server.ehlo()
        
        print("Attempting login...")
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        print("✅ Login SUCCESSFUL!")
        server.quit()
    except Exception as e:
        print(f"❌ Login FAILED: {e}")

if __name__ == "__main__":
    test_raw_smtp()
