
import sqlite3
import os

db_path = 'resume_matching.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = ['users', 'candidate_profiles', 'candidates', 'jobs', 'matches']
print("--- Database Record Counts ---")
for t in tables:
    try:
        count = cursor.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"{t}: {count}")
    except Exception as e:
        print(f"Error querying table {t}: {e}")

print("\n--- Embedding Analysis ---")
try:
    jobs_total = cursor.execute("SELECT count(*) FROM jobs").fetchone()[0]
    jobs_with_emb = cursor.execute("SELECT count(*) FROM jobs WHERE job_embedding IS NOT NULL").fetchone()[0]
    print(f"Jobs with embeddings: {jobs_with_emb}/{jobs_total}")
    
    cand_total = cursor.execute("SELECT count(*) FROM candidates").fetchone()[0]
    cand_with_emb = cursor.execute("SELECT count(*) FROM candidates WHERE resume_embedding IS NOT NULL").fetchone()[0]
    print(f"Candidates with embeddings: {cand_with_emb}/{cand_total}")
except Exception as e:
    print(f"Error analysis embeddings: {e}")

conn.close()
