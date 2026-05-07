import secrets
from passlib.context import CryptContext
import bcrypt

print(f"Bcrypt version: {getattr(bcrypt, '__version__', 'unknown')}")
try:
    print(f"Bcrypt __about__: {getattr(bcrypt, '__about__', 'none')}")
except Exception as e:
    print(f"Error accessing __about__: {e}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    password = secrets.token_urlsafe(32)
    print(f"Generated password length: {len(password)}")
    hashed = pwd_context.hash(password)
    print("Hashing successful!")
except Exception as e:
    print(f"Hashing failed: {type(e).__name__}: {e}")

# Try a very long password
try:
    long_pwd = "a" * 100
    pwd_context.hash(long_pwd)
except Exception as e:
    print(f"Long password failure: {type(e).__name__}: {e}")
