"""
Fix data directly in the database by generating missing embeddings and matches.
This bypasses the API and handles missing OpenAI keys gracefully.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.match import Match
from app.services.nlp_processor import NLPProcessor
from app.services.llm_service import LLMService
from app.services.matching_engine import MatchingEngine
from app.core.config import settings
from loguru import logger

def fix_all():
    db = SessionLocal()
    
    logger.info("Initializing services...")
    nlp_processor = NLPProcessor(
        spacy_model=settings.SPACY_MODEL,
        embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
    )
    llm_service = LLMService()
    matching_engine = MatchingEngine()
    
    # 1. Process Jobs
    logger.info("Checking for jobs missing embeddings...")
    jobs = db.query(Job).filter(Job.job_embedding == None).all()
    for job in jobs:
        try:
            logger.info(f"Generating embedding for job: {job.title}")
            job.job_embedding = nlp_processor.generate_embedding(job.description)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to process job {job.id}: {e}")
            db.rollback()
            
    # 2. Process Candidates
    logger.info("Checking for candidates missing embeddings...")
    candidates = db.query(Candidate).filter(Candidate.resume_embedding == None, Candidate.resume_text != None).all()
    for candidate in candidates:
        try:
            logger.info(f"Generating embedding for candidate: {candidate.name}")
            candidate.resume_embedding = nlp_processor.generate_embedding(candidate.resume_text)
            
            # Also extract skills if missing
            if not candidate.skills:
                candidate.skills = nlp_processor.extract_skills_categorized(candidate.resume_text)
                
            db.commit()
        except Exception as e:
            logger.error(f"Failed to process candidate {candidate.id}: {e}")
            db.rollback()
            
    # 3. Generate Matches (Threshold 0.0)
    logger.info("Generating matches for all combinations...")
    active_jobs = db.query(Job).filter(Job.is_active == True, Job.job_embedding != None).all()
    candidates_ready = db.query(Candidate).filter(Candidate.resume_embedding != None).all()
    
    logger.info(f"Found {len(active_jobs)} ready jobs and {len(candidates_ready)} ready candidates")
    
    matches_created = 0
    for candidate in candidates_ready:
        candidate_data = {
            "embedding": candidate.resume_embedding,
            "skills": candidate.skills or [],
            "experience_years": candidate.experience_years or 0
        }
        
        for job in active_jobs:
            # Check existing
            exists = db.query(Match).filter(Match.candidate_id == candidate.id, Match.job_id == job.id).first()
            if exists:
                continue
                
            job_data = {
                "embedding": job.job_embedding,
                "required_skills": job.required_skills or [],
                "experience_required": job.experience_required or 0,
                "title": job.title
            }
            
            try:
                scores = matching_engine.match_candidate_to_job(candidate_data, job_data)
                
                # Use threshold 0.0 as requested
                if scores["overall_score"] >= 0.0:
                    explanation = "Automatic match generated for data restoration."
                    try:
                        # Only try LLM if key is present
                        if settings.OPENAI_API_KEY:
                            explanation = llm_service.generate_match_explanation(candidate_data, job_data, scores)
                    except:
                        pass
                        
                    match = Match(
                        candidate_id=candidate.id,
                        job_id=job.id,
                        semantic_similarity=scores["semantic_similarity"],
                        skill_overlap_score=scores["skill_overlap_score"],
                        experience_alignment=scores["experience_alignment"],
                        overall_score=scores["overall_score"],
                        match_explanation=explanation
                    )
                    db.add(match)
                    matches_created += 1
            except Exception as e:
                logger.error(f"Match failed for C:{candidate.id}, J:{job.id}: {e}")
                
    db.commit()
    logger.info(f"Successfully created {matches_created} new matches.")
    
    # Final Summary
    total_matches = db.query(Match).count()
    logger.info(f"Total matches in system: {total_matches}")
    
    db.close()

if __name__ == "__main__":
    fix_all()
