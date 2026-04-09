
import sqlite3
import os

db_path = 'resume_matching.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column_if_not_exists(table, column, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"Added column {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding {column}: {e}")

# Columns to add to recruiter_profiles
new_columns = [
    ("roles_hiring_for", "TEXT"),
    ("experience_range", "VARCHAR(100)"),
    ("job_types", "TEXT"),
    ("work_modes", "TEXT"),
    ("default_skills", "TEXT"),
    ("default_location", "VARCHAR(255)"),
    ("default_deadline", "VARCHAR(100)")
]

print("--- Running Migration for recruiter_profiles ---")
for col_name, col_type in new_columns:
    add_column_if_not_exists('recruiter_profiles', col_name, col_type)

conn.commit()
conn.close()
print("Migration completed.")
