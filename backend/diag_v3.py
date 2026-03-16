
import sqlite3
import os

def run():
    print("--- ROBUST DIAGNOSTIC ---")
    # Try multiple possible paths for the DB
    root_dir = r"c:\Users\ADMIN\new-project"
    possible_paths = [
        os.path.join(root_dir, "resume_matching.db"),
        os.path.join(root_dir, "backend", "resume_matching.db"),
        "resume_matching.db"
    ]
    
    db_path = None
    for p in possible_paths:
        if os.path.exists(p):
            db_path = p
            break
            
    if not db_path:
        print("ERROR: Could not find resume_matching.db anywhere!")
        return
        
    print(f"Using DB at: {db_path}")
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, role FROM users LIMIT 10")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} users:")
        for r in rows:
            print(f"  ID: {r[0]} (Type: {type(r[0])}) | Email: {r[1]} | Role: {r[2]}")
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run()
