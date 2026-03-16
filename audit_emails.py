
import sqlite3

db_path = 'resume_matching.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- User Email Audit ---")
user_emails = {row['email']: row['full_name'] for row in cursor.execute("SELECT email, full_name FROM users WHERE role = 'job_seeker'").fetchall()}
candidate_emails = {row['email']: row['name'] for row in cursor.execute("SELECT email, name FROM candidates").fetchall()}

print(f"Users (job_seekers): {len(user_emails)}")
print(f"Candidates (resumes): {len(candidate_emails)}")

print("\n--- Emails in Both ---")
both = set(user_emails.keys()) & set(candidate_emails.keys())
for e in both:
    print(f"MATCH: {e}")

print("\n--- Emails in Users but NOT Candidates (No Resume) ---")
only_users = set(user_emails.keys()) - set(candidate_emails.keys())
for e in only_users:
    print(f"MISSING RESUME: {e} ({user_emails[e]})")

print("\n--- Emails in Candidates but NOT Users (Orphaned Resumes) ---")
only_cand = set(candidate_emails.keys()) - set(user_emails.keys())
for e in only_cand:
    print(f"ORPHANED RESUME: {e} ({candidate_emails[e]})")

conn.close()
