import sys
print(f"Default encoding: {sys.getdefaultencoding()}")
import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "a" * 40
print(f"Password length: {len(password)}")
try:
    pwd_context.hash(password)
    print("Success")
except Exception as e:
    print(f"Failure: {e}")
