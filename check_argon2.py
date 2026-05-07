from passlib.context import CryptContext
try:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    hashed = pwd_context.hash("test_password")
    print("Argon2 success!")
except Exception as e:
    print(f"Argon2 failed: {e}")
