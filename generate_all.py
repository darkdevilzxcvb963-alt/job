
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

from app.core.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.services.matching_engine import MatchingEngine

def generate_all():
    db = SessionLocal()
    try:
        engine = MatchingEngine()
        
        candidates = db.query(Candidate).all()
        jobs = db.query(Job).all()
        
        print(f"Canddiates: {len(candidates)}")
        print(f"Jobs: {len(jobs)}")
        
        for job in jobs:
            print(f"\nProcessing Job: {job.title} ({job.id})")
            if not job.job_embedding:
                print("  Skipping: No embedding")
                continue
                
            job_data = {
                "embedding": job.job_embedding,
                "required_skills": job.required_skills or [],
                "experience_required": job.experience_required or 0,
                "title": job.title
            }
            
            for cand in candidates:
                if not cand.resume_embedding:
                    print(f"  Skipping Candidate {cand.name}: No embedding")
                    continue
                
                # Check for existing valid match
                existing = db.query(Match).filter(
                    Match.candidate_id == cand.id,
                    Match.job_id == job.id
                ).first()
                if existing:
                    print(f"  Match already exists for {cand.name}")
                    continue
                
                cand_data = {
                    "embedding": cand.resume_embedding,
                    "skills": cand.skills or [],
                    "experience_years": cand.experience_years or 0
                }
                
                # Calculate scores
                scores = engine.match_candidate_to_job(cand_data, job_data)
                
                # Threshold zero to match everything for now
                match = Match(
                    candidate_id=cand.id,
                    job_id=job.id,
                    **scores,
                    status='matched'
                )
                db.add(match)
                print(f"  CREATED Match for {cand.name} - Score: {scores['overall_score']:.3f}")
        
        # Cleanup orphaned matches (like the one I found)
        orphaned = db.query(Match).filter(~Match.job_id.in_([j.id for j in jobs])).all()
        if orphaned:
            print(f"\nDeleting {len(orphaned)} orphaned matches...")
            for o in orphaned:
                db.delete(o)
                
        db.commit()
        print("\nProcessing Complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_all()
