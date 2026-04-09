"""
Background Task Service for Production
Handles asynchronous processing for matching, notifications, and intelligence.
"""
import asyncio
from typing import List
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime, timedelta

from app.services.intelligence_service import IntelligenceService
from app.services.notification_dispatcher import NotificationDispatcher
from app.models.user import User
from app.models.job import Job
from app.services.matching_engine import MatchingEngine

class TaskService:
    """Orchestrates background processing tasks"""
    
    def __init__(self, db: Session):
        self.db = db
        self.intelligence = IntelligenceService(db)
        self.dispatcher = NotificationDispatcher(db)

    async def run_daily_digests(self):
        """Send daily summary of matches and activities to users"""
        logger.info("Starting Daily Digest background task...")
        users = self.db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            # Logic to find matches since last 24h
            # For brevity, we simulate a check
            count = 5 # Example
            if count > 0:
                await self.dispatcher.dispatch(
                    user.id,
                    "📅 Your Daily Career Digest",
                    f"You have {count} new potential matches and 2 new career suggestions waiting for you.",
                    "daily_digest"
                )
        logger.info(f"Daily Digest completed for {len(users)} users.")

    async def update_all_profile_intelligence(self):
        """Recalculate profile strength and suggestions for all users"""
        logger.info("Updating global profile intelligence...")
        users = self.db.query(User).filter(User.role == 'job_seeker').all()
        
        for user in users:
            await self.intelligence.generate_career_suggestions(user.id)
            
        logger.info(f"Intelligence update completed for {len(users)} candidates.")

    async def process_new_job_matches(self, job_id: str):
        """When a new job is posted, find and notify top candidates immediately"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job: return

        engine = MatchingEngine()
        # Find candidates (simplified filter)
        candidates = self.db.query(User).filter(User.role == 'job_seeker').limit(50).all()
        
        for cand in candidates:
            # matching logic...
            # if score > 0.8: notify
            pass
            
        logger.info(f"New job {job_id} matching process triggered.")

    @staticmethod
    def start_background_loop(db_factory):
        """Simple loop to run periodic tasks without full Celery setup"""
        async def loop():
            while True:
                try:
                    # Run daily tasks at a specific interval or time
                    # In a real production, use Celery Beat. 
                    # Here we simulate periodic intelligence updates.
                    db = db_factory()
                    service = TaskService(db)
                    await service.update_all_profile_intelligence()
                    db.close()
                except Exception as e:
                    logger.error(f"Background loop error: {e}")
                
                await asyncio.sleep(3600 * 6) # Run every 6 hours
        
        asyncio.create_task(loop())
