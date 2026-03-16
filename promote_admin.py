import sqlite3
conn = sqlite3.connect('backend/resume_matching.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'apitest@example.com'")
conn.commit()
print("Updated apitest@example.com to admin")
conn.close()
