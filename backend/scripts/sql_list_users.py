import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resume_matching.db'))
print('DB path:', db_path)
if not os.path.exists(db_path):
    print('DB file not found')
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
try:
    cur.execute('SELECT id, email, role, is_active, is_verified, last_login FROM users')
    rows = cur.fetchall()
    if not rows:
        print('No users')
    else:
        for r in rows:
            print(r)
finally:
    conn.close()
