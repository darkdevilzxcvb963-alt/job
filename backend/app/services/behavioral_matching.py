"""
Behavioral Matching Service for Production
Combines structural matching with user interaction patterns
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from loguru import logger

from app.models.profile_settings import UserActivityLog, AISettings
from app.services.matching_engine import MatchingEngine

class BehavioralMatchingService:
    """Service to inject behavioral intelligence into the matching engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.engine = MatchingEngine()

    async def get_behavioral_score(self, user_id: str, job_id: str, job_category: str = None) -> float:
        """
        Calculate a behavioral score based on historical interactions
        1.0 = positive bias (user likes this type of job)
        0.5 = neutral
        0.0 = negative bias (user skips this type of job)
        """
        # 1. Direct interactions with this job
        direct_actions = self.db.query(UserActivityLog).filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.entity_id == job_id
        ).all()
        
        # If user already skipped/disliked, return low
        if any(a.action in ['skip', 'dislike'] for a in direct_actions):
            return 0.1
        if any(a.action in ['like', 'apply', 'save'] for a in direct_actions):
            return 1.0

        # 2. Category-based interactions
        if job_category:
            actions = self.db.query(UserActivityLog).filter(
                UserActivityLog.user_id == user_id,
                UserActivityLog.extra_data['category'].astext == job_category
            ).all()
            
            if not actions:
                return 0.5
                
            pos = sum(1 for a in actions if a.action in ['apply', 'save', 'like'])
            neg = sum(1 for a in actions if a.action in ['skip', 'dislike'])
            
            total = pos + neg
            if total > 0:
                return (pos / total) * 0.5 + 0.25 # Scale to 0.25 - 0.75 range
                
        return 0.5

    async def get_hybrid_match(self, user_id: str, candidate_data: Dict, job_data: Dict) -> Dict:
        """
        Calculates a hybrid score: Structural (MatchingEngine) + Behavioral (Interactions)
        """
        # 1. Get structural score
        structural_results = self.engine.match_candidate_to_job(candidate_data, job_data)
        base_score = structural_results['overall_score']
        
        # 2. Get behavioral modifier
        behavioral_score = await self.get_behavioral_score(
            user_id, 
            job_data.get('id'), 
            job_data.get('category')
        )
        
        # 3. Get user-defined AI weights from settings
        ai_settings = self.db.query(AISettings).filter(AISettings.user_id == user_id).first()
        
        alpha = 0.7 # Weight for structural
        beta = 0.3  # Weight for behavioral
        
        # Simple hybrid formula
        hybrid_score = (alpha * base_score) + (beta * behavioral_score)
        
        # Log for debugging
        logger.debug(f"Hybrid Match [User:{user_id} Job:{job_data.get('id')}]: Base={base_score:.2f}, Behavior={behavioral_score:.2f}, Final={hybrid_score:.2f}")
        
        structural_results['behavioral_score'] = behavioral_score
        structural_results['hybrid_score'] = hybrid_score
        structural_results['match_explanation'] = self._generate_explanation(structural_results)
        
        return structural_results

    def _generate_explanation(self, results: Dict) -> str:
        """Generate a human-readable explanation for the hybrid score"""
        reasons = []
        if results.get('semantic_similarity', 0) > 0.8:
            reasons.append("Strong semantic fit with the job description")
        if results.get('skill_overlap_score', 0) > 0.7:
            reasons.append("High overlap with required technical skills")
        if results.get('behavioral_score', 0) > 0.7:
            reasons.append("Matches your recent interests and job interaction patterns")
        elif results.get('behavioral_score', 0) < 0.4:
            reasons.append("Lower score due to previous skips of similar roles")
            
        return " | ".join(reasons) if reasons else "Moderate match across multiple factors"

    @staticmethod
    async def record_activity(db: Session, user_id: str, action: str, entity_id: str, entity_type: str = "job", category: str = None):
        """Record a user interaction for future matching"""
        log = UserActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            extra_data={"category": category} if category else None
        )
        db.add(log)
        db.commit()
        return True
