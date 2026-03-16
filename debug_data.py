
import sqlite3
import json

db_path = 'resume_matching.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- Job Detals ---")
jobs = cursor.execute("SELECT id, title, recruiter_id, job_embedding FROM jobs").fetchall()
for j in jobs:
    has_emb = "Yes" if j['job_embedding'] else "No"
    print(f"ID: {j['id']}, Title: {j['title']}, Recruiter: {j['recruiter_id']}, Embedding: {has_emb}")

print("\n--- Candidate Details ---")
candidates = cursor.execute("SELECT id, name, email, resume_embedding FROM candidates").fetchall()
for c in candidates:
    has_emb = "Yes" if c['resume_embedding'] else "No"
    print(f"ID: {c['id']}, Name: {c['name']}, Email: {c['email']}, Embedding: {has_emb}")

print("\n--- Match Details ---")
matches = cursor.execute("SELECT * FROM matches").fetchall()
for m in matches:
    print(dict(m))

conn.close()
