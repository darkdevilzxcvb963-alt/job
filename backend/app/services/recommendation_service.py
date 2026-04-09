"""
Proactive Recommendation Service
Automates the discovery of matches between candidates and jobs.
"""
from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.models.job import Job
from app.api.v1.candidates import generate_matches_task
from loguru import logger
import asyncio

class RecommendationService:
    """Service to handle automated proactive matching"""
    
    def __init__(self, db: Session):
        self.db = db

    async def run_global_matching(self):
        """Run matching for all active candidates against all active jobs"""
        logger.info("Starting global proactive matching cycle...")
        
        candidates = self.db.query(Candidate).all()
        logger.info(f"Scanning {len(candidates)} candidates for new matches.")
        
        for candidate in candidates:
            # We use the existing background task logic which is now optimized with VectorStore
            try:
                # Run in a thread to keep async event loop free if needed,
                # but since it's a background task already we just call it.
                # In a real production system, this would be a Celery task.
                generate_matches_task(candidate.id)
            except Exception as e:
                logger.error(f"Error matching candidate {candidate.id}: {e}")
        
        logger.info("Global proactive matching cycle complete.")

    async def run_job_matching(self, job_id: str):
        """Specifically match all candidates against a newly posted job"""
        from app.api.v1.matches import generate_matches_for_job_task
        generate_matches_for_job_task(job_id)
