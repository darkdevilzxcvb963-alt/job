import sqlite3

conn = sqlite3.connect('resume_matching.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users)")
cols = cursor.fetchall()

print("\nDatabase Schema - users table:")
print("=" * 40)
for col in cols:
    print(f"{col[1]:30} {col[2]}")

conn.close()
