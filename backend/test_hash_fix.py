import sys
import os
sys.path.append(os.getcwd())

from app.core.security import pwd_context

def test_argon2_recognition():
    argon2_hash = "$argon2id$v=19$m=65536,t=3,p=4$6mlyOndid3Y3cm56cHZ4aw$wO4vK6v8f9N9hY/gD2f2+vVf5z4Nl8mYn/QjR7v4l9M"
    
    try:
        scheme = pwd_context.identify(argon2_hash)
        print(f"Identified scheme: {scheme}")
        if scheme == "argon2":
            print("SUCCESS: Identified argon2 hash!")
        else:
            print(f"FAILURE: Identified as {scheme} instead of argon2.")
    except Exception as e:
        print(f"ERROR identifying hash: {e}")

if __name__ == "__main__":
    test_argon2_recognition()
