import sqlite3
import os

def check_db(path):
    if not os.path.exists(path):
        return "Not found"
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        counts = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except:
                pass
        conn.close()
        return f"Tables: {len(tables)}, Row Counts: {counts}"
    except Exception as e:
        return f"Error: {e}"

print(f"ROOT DB: {check_db('resume_matching.db')}")
print(f"BACKEND DB: {check_db('backend/resume_matching.db')}")
