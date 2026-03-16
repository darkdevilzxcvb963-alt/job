import sqlite3
import os

db_path = 'backend/resume_matching.db'
email_to_check = 'srihariharan26ias@gmail.com'

if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT email, is_verified, is_active, role FROM users WHERE email = ?", (email_to_check,))
    user = cursor.fetchone()
    
    if user:
        print(f"USER FOUND:")
        print(f"  Email: {user[0]}")
        print(f"  Verified: {bool(user[1])}")
        print(f"  Active: {bool(user[2])}")
        print(f"  Role: {user[3]}")
    else:
        print(f"USER NOT FOUND: {email_to_check}")
        
        # List all emails to help user see what IS there
        cursor.execute("SELECT email FROM users LIMIT 10")
        all_emails = cursor.fetchall()
        print("\nExisting Emails (Sample):")
        for e in all_emails:
            print(f"  - {e[0]}")
            
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    conn.close()
