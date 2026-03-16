from app.core.config import settings
import os

print(f"Current Working Directory: {os.getcwd()}")
print(f"MAIL_USERNAME: '{settings.MAIL_USERNAME}'")
print(f"MAIL_PASSWORD: '{'********' if settings.MAIL_PASSWORD else ''}'")
print(f"DATABASE_URL: {settings.DATABASE_URL}")

if not settings.MAIL_USERNAME:
    print("❌ MAIL_USERNAME is empty! .env file probably not loaded.")
    # Check if .env exists in backend/
    if os.path.exists('backend/.env'):
        print("✅ Found .env in backend/ directory.")
    else:
        print("❌ .env NOT found in backend/ directory.")
else:
    print("✅ MAIL_USERNAME is set! .env file loaded successfully.")
