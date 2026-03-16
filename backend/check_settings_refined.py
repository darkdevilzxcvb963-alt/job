import os
from dotenv import load_dotenv

print(f"Current Working Directory: {os.getcwd()}")
print(f"Pre-load MAIL_USERNAME: '{os.environ.get('MAIL_USERNAME')}'")

# Try to load from current directory
load_dotenv()
print(f"Post-load(default) MAIL_USERNAME: '{os.environ.get('MAIL_USERNAME')}'")

# Try to load from backend/.env explicitly
load_dotenv('backend/.env')
print(f"Post-load(backend/.env) MAIL_USERNAME: '{os.environ.get('MAIL_USERNAME')}'")

from app.core.config import settings
print(f"Final settings.MAIL_USERNAME: '{settings.MAIL_USERNAME}'")
