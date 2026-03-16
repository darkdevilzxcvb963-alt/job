import sqlite3
import json
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), "..", "resume_matching.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

result = {}

# Count users
cursor.execute("SELECT COUNT(*) FROM users")
result["total_users"] = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM users WHERE role='job_seeker'")
result["job_seekers"] = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM users WHERE role='recruiter'")
result["recruiters"] = cursor.fetchone()[0]

# Count jobs
cursor.execute("SELECT COUNT(*) FROM jobs")
result["total_jobs"] = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active=1")
result["active_jobs"] = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_embedding IS NOT NULL")
result["jobs_with_embeddings"] = cursor.fetchone()[0]

# Count candidates
cursor.execute("SELECT COUNT(*) FROM candidates")
result["total_candidates"] = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM candidates WHERE resume_embedding IS NOT NULL")
result["candidates_with_embeddings"] = cursor.fetchone()[0]

# Count matches
cursor.execute("SELECT COUNT(*) FROM matches")
result["total_matches"] = cursor.fetchone()[0]

# Get sample data
cursor.execute("SELECT id, title, company, is_active, job_embedding IS NOT NULL as has_emb FROM jobs LIMIT 3")
result["sample_jobs"] = [{"id": row[0], "title": row[1], "company": row[2], "active": bool(row[3]), "has_embedding": bool(row[4])} for row in cursor.fetchall()]

cursor.execute("SELECT id, name, email, resume_embedding IS NOT NULL as has_emb FROM candidates LIMIT 3")
result["sample_candidates"] = [{"id": row[0], "name": row[1], "email": row[2], "has_embedding": bool(row[3])} for row in cursor.fetchall()]

cursor.execute("SELECT id, candidate_id, job_id, overall_score FROM matches LIMIT 3")
result["sample_matches"] = [{"id": row[0], "candidate_id": row[1], "job_id": row[2], "score": row[3]} for row in cursor.fetchall()]

conn.close()

# Write to JSON
with open("diagnostic_result.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
