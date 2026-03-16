
import sys
import os
import sqlite3
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

from app.services.matching_engine import MatchingEngine

def generate_raw():
    db_path = 'resume_matching.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    engine = MatchingEngine()
    
    # 1. Get candidates with embeddings
    candidates = cursor.execute("SELECT id, name, email, resume_embedding, skills, experience_years FROM candidates WHERE resume_embedding IS NOT NULL").fetchall()
    
    # 2. Get jobs with embeddings
    jobs = cursor.execute("SELECT id, title, job_embedding, required_skills, experience_required FROM jobs WHERE job_embedding IS NOT NULL").fetchall()
    
    print(f"Eligible Candidates: {len(candidates)}")
    print(f"Eligible Jobs: {len(jobs)}")
    
    match_count = 0
    for job in jobs:
        job_emb = json.loads(job['job_embedding']) if isinstance(job['job_embedding'], str) else job['job_embedding']
        job_data = {
            "embedding": job_emb,
            "required_skills": json.loads(job['required_skills']) if isinstance(job['required_skills'], str) else job['required_skills'] or [],
            "experience_required": job['experience_required'] or 0,
            "title": job['title']
        }
        
        for cand in candidates:
            cand_emb = json.loads(cand['resume_embedding']) if isinstance(cand['resume_embedding'], str) else cand['resume_embedding']
            cand_skills = json.loads(cand['skills']) if isinstance(cand['skills'], str) else cand['skills'] or []
            
            cand_data = {
                "embedding": cand_emb,
                "skills": cand_skills,
                "experience_years": cand['experience_years'] or 0
            }
            
            # Check if match exists
            exists = cursor.execute("SELECT count(*) FROM matches WHERE candidate_id = ? AND job_id = ?", (cand['id'], job['id'])).fetchone()[0]
            if exists:
                print(f"  Match exists for {cand['name']}")
                continue
                
            # Calculate score
            scores = engine.match_candidate_to_job(cand_data, job_data)
            
            # Insert match
            import uuid
            from datetime import datetime
            match_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO matches 
                (id, candidate_id, job_id, semantic_similarity, skill_overlap_score, experience_alignment, overall_score, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id, cand['id'], job['id'], 
                scores['semantic_similarity'], scores['skill_overlap_score'], 
                scores['experience_alignment'], scores['overall_score'], 
                'matched', now, now
            ))
            match_count += 1
            print(f"  CREATED Match: {cand['name']} <-> {job['title']} (Score: {scores['overall_score']:.3f})")

    # Deleting orphaned matches
    job_ids = [j['id'] for j in jobs]
    if job_ids:
        placeholders = ','.join(['?'] * len(job_ids))
        cursor.execute(f"DELETE FROM matches WHERE job_id NOT IN ({placeholders})", job_ids)

    conn.commit()
    conn.close()
    print(f"\nProcessing Complete. Created {match_count} matches.")

if __name__ == "__main__":
    generate_raw()
