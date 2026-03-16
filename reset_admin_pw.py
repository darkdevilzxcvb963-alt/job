import sqlite3
from app.core.security import get_password_hash
import os

db_path = 'backend/resume_matching.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
new_hash = get_password_hash("TestPassword123")
cursor.execute("UPDATE users SET hashed_password = ? WHERE email = 'apitest@example.com'", (new_hash,))
conn.commit()
print("Reset password for apitest@example.com")
conn.close()
