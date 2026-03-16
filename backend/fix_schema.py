"""
Fix database schema by adding missing columns to jobs table
"""
import sqlite3
import os

# Find the correct database file
db_paths = [
    "c:/Users/ADMIN/new-project/backend/resume_matching.db",
    "c:/Users/ADMIN/new-project/resume_matching.db",
]

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Found database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        print(f"Current columns: {', '.join(col_names)}")
        
        # Add missing columns if they don't exist
        if 'skills_by_category' not in col_names:
            print("Adding skills_by_category column...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN skills_by_category TEXT")
            print("✅ Added skills_by_category column")
        else:
            print("✅ skills_by_category column already exists")
        
        if 'preferred_skills' not in col_names:
            print("Adding preferred_skills column...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN preferred_skills TEXT")
            print("✅ Added preferred_skills column")
        else:
            print("✅ preferred_skills column already exists")
            
        if 'education_required' not in col_names:
            print("Adding education_required column...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN education_required TEXT")
            print("✅ Added education_required column")
        else:
            print("✅ education_required column already exists")
        
        conn.commit()
        
        # Verify
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        print(f"\nFinal columns: {', '.join(col_names)}")
        
        conn.close()
        print(f"\n✅ Database schema updated successfully at {db_path}\n")
    else:
        print(f"Database not found at: {db_path}")
