"""
Deep dive debug: Compare DB matches vs API matches for a single job logic.
"""
import requests
import sqlite3
import sys
from app.core.database import SessionLocal
from app.models.match import Match
from app.models.job import Job
from app.models.candidate import Candidate

def debug_interaction():
    print("="*60)
    print("DEBUG: API vs DB")
    print("="*60)
    
    # 1. Get a job ID with matches from DB directly
    db_session = SessionLocal()
    
    # Check raw SQL first
    conn = sqlite3.connect('../resume_matching.db')
    c = conn.cursor()
    c.execute("SELECT job_id, count(*) FROM matches GROUP BY job_id ORDER BY count(*) DESC LIMIT 1")
    row = c.fetchone()
    if not row:
        print("❌ No matches in DB (Raw SQL check)")
        return
        
    job_id = row[0]
    count = row[1]
    print(f"Target Job ID: {job_id}")
    print(f"Expected Matches: {count}")
    
    # 2. Check via SQLAlchemy (to mimic API logic)
    print("\n[SQLAlchemy Check]")
    matches = db_session.query(Match).filter(Match.job_id == job_id).all()
    print(f"Found {len(matches)} matches via SQLAlchemy")
    
    if len(matches) > 0:
        m = matches[0]
        print(f"Sample Match: Job={m.job_id}, Cand={m.candidate_id}")
        
        # Mimic the loop in matches.py
        job = db_session.query(Job).filter(Job.id == m.job_id).first()
        cand = db_session.query(Candidate).filter(Candidate.id == m.candidate_id).first()
        
        print(f"Job Lookup: {'Found' if job else 'Missing'}")
        print(f"Candidate Lookup: {'Found' if cand else 'Missing'}")
        
        if not job or not cand:
            print("❌ FILTERING WOULD HAPPEN HERE! The API drops matches if job/cand is missing.")
            
    # 3. Check min_score handling
    print("\n[Min Score Check]")
    low_matches = db_session.query(Match).filter(Match.job_id == job_id).filter(Match.overall_score >= 0.0).all()
    print(f"Matches with score >= 0.0: {len(low_matches)}")
    
    db_session.close()
    conn.close()

if __name__ == "__main__":
    debug_interaction()
