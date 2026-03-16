import sys
import os
import uuid
import sqlite3
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.nlp_processor import NLPProcessor
from app.core.config import settings

print("DEBUG: Starting SQL Seeding script...")

# 1. Initialize NLP
print("DEBUG: Initializing NLP...")
nlp = NLPProcessor(
    spacy_model=settings.SPACY_MODEL,
    embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
)

# 2. Define Jobs
jobs_to_seed = [
    {
        "title": "Senior Solutions Architect",
        "company": "Global Tech",
        "location": "Remote",
        "description": "Expert in AWS, distributed systems, and Python. Lead cloud-native transformations and mentoring engineering teams. Strong knowledge of cybersecurity and risk assessment.",
        "required_skills": ["Python", "AWS", "Cybersecurity", "Strategic Planning", "Technical Writing"],
        "experience_required": 8,
        "job_type": "full-time"
    },
    {
        "title": "Frontend Developer",
        "company": "Visual Arts",
        "location": "Hybrid",
        "description": "Looking for a React expert with strong UI/UX design skills. Experience with Figma, Adobe Photoshop, and modern CSS frameworks. Collaborative team player with Agile experience.",
        "required_skills": ["React", "JavaScript", "Figma", "UI/UX Design", "Agile Methodology"],
        "experience_required": 3,
        "job_type": "full-time"
    }
]

# 3. Connect to SQLite
db_path = os.path.join(os.getcwd(), "resume_matching.db")
print(f"DEBUG: Connecting to {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    for data in jobs_to_seed:
        print(f"DEBUG: Processing {data['title']}...")
        job_id = str(uuid.uuid4())
        
        # Generate embedding
        print("DEBUG: Generating embedding...")
        embedding = nlp.generate_embedding(data["description"])
        
        # Insert using raw SQL
        print("DEBUG: Executing SQL Insert...")
        cursor.execute(
            """
            INSERT INTO jobs 
            (id, title, company, description, required_skills, experience_required, location, job_type, job_embedding, is_active, posted_at, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'), datetime('now'))
            """,
            (
                job_id,
                data["title"],
                data["company"],
                data["description"],
                json.dumps(data["required_skills"]),
                data["experience_required"],
                data["location"],
                data["job_type"],
                json.dumps(embedding)
            )
        )
        print(f"✓ Job {data['title']} inserted.")

    conn.commit()
    print("✓ All jobs seeded successfully via SQL!")
except Exception as e:
    print(f"❌ SQL Error: {e}")
    conn.rollback()
finally:
    conn.close()
