import sqlite3
import os
import sys

# Add backend directory to path to use internal modules if needed, 
# but direct SQL is safer here for quick manual entry
db_path = 'backend/resume_matching.db'
email = 'srihariharan26ias@gmail.com'
full_name = 'Sri Hari Haran'
password_hash = '$argon2id$v=19$m=65536,t=3,p=4$693iEOnYpLzK3XhGv6uY+Q$RvhF8m6zVp0u7W83pY6uJQ' # Simple hash for 'TestPassword123'

if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        print(f"User {email} already exists.")
    else:
        import uuid
        user_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (id, full_name, email, hashed_password, role, is_active, is_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (user_id, full_name, email, password_hash, 'job_seeker', 1, 1))
        conn.commit()
        print(f"SUCCESS: User {email} added to database!")
        print(f"You can now use the 'Forgot Password' feature with this email.")
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    conn.close()
