
import sqlite3
import os
from jose import jwt
from datetime import datetime, timedelta

# Hardcoded settings from app/core/config.py for diagnostic
SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"

def run_diagnostic():
    db_path = "resume_matching.db"
    print(f"Checking DB at: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: DB file not found at {db_path}")
        # Try parent or backend
        if os.path.exists("backend/resume_matching.db"):
             db_path = "backend/resume_matching.db"
        elif os.path.exists("../resume_matching.db"):
             db_path = "../resume_matching.db"
        else:
            print("Could not find resume_matching.db")
            return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check users table
        print("\n--- Users Table ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("ERROR: 'users' table not found!")
            return
            
        cursor.execute("SELECT id, email, role, is_verified, is_active FROM users")
        users = cursor.fetchall()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"  ID: {u[0]} | Email: {u[1]} | Role: {u[2]} | Verified: {u[3]} | Active: {u[4]}")
            
        if not users:
            print("No users found.")
            return
            
        # 2. Test JWT Logic
        print("\n--- JWT Logic ---")
        test_user_id = users[0][0]
        test_user_email = users[0][1]
        
        payload = {
            "sub": test_user_id,
            "role": users[0][2],
            "exp": datetime.utcnow() + timedelta(minutes=60),
            "type": "access"
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        print(f"Generated token for {test_user_email} (ID: {test_user_id})")
        
        # Verify
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"Successfully decoded token. Sub: {decoded.get('sub')} (Type: {type(decoded.get('sub'))})")
            
            # Match with DB type
            db_id = test_user_id
            print(f"DB ID type: {type(db_id)}")
            if str(decoded.get('sub')) == str(db_id):
                print("Token sub matches DB ID (string comparison)")
            else:
                print("ERROR: Token sub DOES NOT MATCH DB ID")
        except Exception as e:
            print(f"Token decode failed: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    run_diagnostic()
