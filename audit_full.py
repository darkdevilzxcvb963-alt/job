
import sqlite3

db_path = 'resume_matching.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

output = []

def log(msg):
    print(msg)
    output.append(msg)

log("--- USERS ---")
users = cursor.execute("SELECT id, email, full_name, role FROM users").fetchall()
user_map = {}
for u in users:
    log(f"ID: {u['id']}, Email: {u['email']}, Role: {u['role']}, Name: {u['full_name']}")
    user_map[u['id']] = u['email']

log("\n--- CANDIDATES ---")
candidates = cursor.execute("SELECT id, email, name FROM candidates").fetchall()
for c in candidates:
    log(f"ID: {c['id']}, Email: {c['email']}, Name: {c['name']}")

log("\n--- JOBS ---")
jobs = cursor.execute("SELECT id, title, recruiter_id FROM jobs").fetchall()
for j in jobs:
    recruiter_email = user_map.get(j['recruiter_id'], 'UNKNOWN')
    log(f"ID: {j['id']}, Title: {j['title']}, RecruiterID: {j['recruiter_id']} (Email: {recruiter_email})")

log("\n--- MATCHES ---")
matches = cursor.execute("SELECT m.id, m.candidate_id, m.job_id, m.overall_score, c.email as c_email, j.title as j_title FROM matches m JOIN candidates c ON m.candidate_id = c.id JOIN jobs j ON m.job_id = j.id").fetchall()
for m in matches:
    log(f"MatchID: {m['id']}, Candidate Email: {m['c_email']}, Job: {m['j_title']}, Score: {m['overall_score']}")

with open('audit_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

conn.close()
