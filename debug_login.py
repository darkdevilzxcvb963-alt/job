import sqlite3
conn = sqlite3.connect('backend/resume_matching.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE email = 'apitest@example.com'")
user = cursor.fetchone()
if user:
    for key in user.keys():
        print(f"{key}: {user[key]}")
else:
    print("User not found")
conn.close()
