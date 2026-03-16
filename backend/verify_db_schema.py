import sqlite3
import os

db_path = "c:/Users/ADMIN/new-project/resume_matching.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(jobs)")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    print(f"Columns: {', '.join(col_names)}")
    if 'skills_by_category' in col_names:
        print("SUCCESS: 'skills_by_category' column found.")
    else:
        print("FAILURE: 'skills_by_category' column NOT found.")
    conn.close()
