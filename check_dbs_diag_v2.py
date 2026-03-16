import sqlite3
import os

def check_db(path):
    if not os.path.exists(path):
        return "Not found"
    try:
        size = os.path.getsize(path)
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        info = f"Size: {size}, Tables: {len(tables)}"
        if tables:
            info += f" ({', '.join(tables)})"
            
            counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                except:
                    pass
            info += f"\nCounts: {counts}"
        conn.close()
        return info
    except Exception as e:
        return f"Error: {e}"

paths = [
    'resume_matching.db',
    'backend/resume_matching.db',
    'backend/app.db'
]

for p in paths:
    print(f"--- {p} ---")
    print(check_db(p))
    print()
