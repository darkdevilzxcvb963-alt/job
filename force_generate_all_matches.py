
import sys
import os
from pathlib import Path
from loguru import logger

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

from app.core.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.services.nlp_processor import NLPProcessor
from app.services.matching_engine import MatchingEngine
from app.core.config import settings

def force_generate():
    db = SessionLocal()
    try:
        # Initialize services
        nlp = NLPProcessor(
            spacy_model=settings.SPACY_MODEL,
            embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
        )
        engine = MatchingEngine()
        
        # 1. Fix missing candidate embeddings
        candidates = db.query(Candidate).all()
        print(f"Checking {len(candidates)} candidates for missing embeddings...")
        
        for cand in candidates:
            if not cand.resume_embedding:
                if cand.resume_text:
                    print(f"Generating embedding for: {cand.name} ({cand.email})")
                    try:
                        cand.resume_embedding = nlp.generate_embedding(cand.resume_text)
                        db.commit()
                        print(f"  Successfully generated embedding.")
                    except Exception as e:
                        print(f"  Error generating embedding for {cand.name}: {e}")
                else:
                    print(f"  Skipping {cand.name}: No resume text found.")
        
        # 2. Fix missing job embeddings (though audit said 1/1, good to be sure)
        jobs = db.query(Job).all()
        print(f"\nChecking {len(jobs)} jobs for missing embeddings...")
        for job in jobs:
            if not job.job_embedding:
                if job.description:
                    print(f"Generating embedding for job: {job.title}")
                    try:
                        job.job_embedding = nlp.generate_embedding(job.description)
                        db.commit()
                    except Exception as e:
                        print(f"  Error generating job embedding: {e}")
        
        # 3. Generate matches
        print(f"\nGenerating matches for {len(jobs)} jobs and {len(candidates)} candidates...")
        match_count = 0
        for job in jobs:
            if not job.job_embedding: continue
            
            job_data = {
                "embedding": job.job_embedding,
                "required_skills": job.required_skills or [],
                "experience_required": job.experience_required or 0,
                "title": job.title
            }
            
            for cand in candidates:
                if not cand.resume_embedding: continue
                
                # Check if match already exists
                existing = db.query(Match).filter(
                    Match.candidate_id == cand.id,
                    Match.job_id == job.id
                ).first()
                
                if existing:
                    print(f"  Match already exists for {cand.name} <-> {job.title} (Score: {existing.overall_score:.2f})")
                    continue
                
                # Calculate match
                cand_data = {
                    "embedding": cand.resume_embedding,
                    "skills": cand.skills or [],
                    "experience_years": cand.experience_years or 0
                }
                
                scores = engine.match_candidate_to_job(cand_data, job_data)
                
                # We'll be more inclusive during manual fix (threshold 0.05)
                if scores['overall_score'] >= 0.05:
                    match = Match(
                        candidate_id=cand.id,
                        job_id=job.id,
                        **scores,
                        status='matched'
                    )
                    db.add(match)
                    match_count += 1
                    print(f"  CREATED Match: {cand.name} <-> {job.title} (Score: {scores['overall_score']:.2f})")
        
        db.commit()
        print(f"\nSUCCESS: Generated {match_count} new matches.")
        
    except Exception as e:
        print(f"Critical error during force generation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    force_generate()
