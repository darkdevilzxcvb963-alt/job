
import sqlite3

db_path = 'resume_matching.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- Recruiter & Admin Users ---")
users = cursor.execute("SELECT id, full_name, email, role FROM users WHERE role IN ('recruiter', 'admin')").fetchall()
for u in users:
    print(f"ID: {u['id']}, Name: {u['full_name']}, Email: {u['email']}, Role: {u['role']}")

print("\n--- Job Ownership ---")
jobs = cursor.execute("SELECT id, title, recruiter_id FROM jobs").fetchall()
for j in jobs:
    print(f"Job ID: {j['id']}, Title: {j['title']}, Recruiter ID: {j['recruiter_id']}")

print("\n--- Match Ownership ---")
matches = cursor.execute("SELECT m.id, m.candidate_id, m.job_id, m.overall_score, j.recruiter_id, c.email as candidate_email FROM matches m JOIN jobs j ON m.job_id = j.id JOIN candidates c ON m.candidate_id = c.id").fetchall()
for m in matches:
    print(f"Match ID: {m['id']}, Candidate: {m['candidate_email']}, Job Recruiter: {m['recruiter_id']}, Score: {m['overall_score']}")

conn.close()
