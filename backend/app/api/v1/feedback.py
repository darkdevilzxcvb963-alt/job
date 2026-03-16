"""
Match Feedback & Analytics API
Provides feedback mechanisms and analytics endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from loguru import logger

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.match import Match
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.user import User

router = APIRouter()

# ─── Feedback Models ─────────────────────────────────────────────────────────

class MatchFeedback(BaseModel):
    rating: int  # 1-5 stars or -1 (thumbs down), 1 (thumbs up)
    reason: Optional[str] = None  # "not_relevant", "wrong_skills", "wrong_location", etc.

class FeedbackResponse(BaseModel):
    match_id: str
    rating: int
    message: str

# ─── Feedback Endpoints ──────────────────────────────────────────────────────

@router.post("/{match_id}/feedback", response_model=FeedbackResponse)
async def submit_match_feedback(
    match_id: str,
    feedback: MatchFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a match quality (thumbs up/down or star rating).
    Used to improve scoring algorithms over time.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Store feedback as metadata on the match
    match.feedback_rating = feedback.rating
    match.feedback_reason = feedback.reason
    match.feedback_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Feedback received for match {match_id}: rating={feedback.rating}, reason={feedback.reason}")
    
    return FeedbackResponse(
        match_id=match_id,
        rating=feedback.rating,
        message="Thank you for your feedback! This helps us improve match quality."
    )

# ─── Analytics Endpoints ─────────────────────────────────────────────────────

@router.get("/analytics/skill-demand")
async def get_skill_demand(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated skill demand data from active job postings.
    Returns which skills are most in-demand.
    """
    jobs = db.query(Job).filter(Job.is_active == True).all()
    
    skill_counts = {}
    for job in jobs:
        skills = job.required_skills or []
        for skill in skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Sort by count descending
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        "top_skills": [{"skill": s, "demand_count": c} for s, c in sorted_skills],
        "total_active_jobs": len(jobs)
    }

@router.get("/analytics/match-quality")
async def get_match_quality_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregate statistics on match quality and feedback.
    """
    total_matches = db.query(func.count(Match.id)).scalar() or 0
    
    # Score distribution
    excellent = db.query(func.count(Match.id)).filter(Match.overall_score >= 0.8).scalar() or 0
    good = db.query(func.count(Match.id)).filter(
        and_(Match.overall_score >= 0.6, Match.overall_score < 0.8)
    ).scalar() or 0
    fair = db.query(func.count(Match.id)).filter(
        and_(Match.overall_score >= 0.4, Match.overall_score < 0.6)
    ).scalar() or 0
    low = db.query(func.count(Match.id)).filter(Match.overall_score < 0.4).scalar() or 0
    
    # Average scores
    avg_overall = db.query(func.avg(Match.overall_score)).scalar() or 0
    avg_semantic = db.query(func.avg(Match.semantic_similarity)).scalar() or 0
    avg_skill = db.query(func.avg(Match.skill_overlap_score)).scalar() or 0
    
    return {
        "total_matches": total_matches,
        "score_distribution": {
            "excellent_80_plus": excellent,
            "good_60_80": good,
            "fair_40_60": fair,
            "low_under_40": low
        },
        "averages": {
            "overall": round(float(avg_overall), 3),
            "semantic_similarity": round(float(avg_semantic), 3),
            "skill_overlap": round(float(avg_skill), 3)
        }
    }

@router.get("/analytics/recruitment-funnel")
async def get_recruitment_funnel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track candidates through the recruitment funnel.
    """
    total_candidates = db.query(func.count(Candidate.id)).scalar() or 0
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    total_matches = db.query(func.count(Match.id)).scalar() or 0
    applied = db.query(func.count(Match.id)).filter(Match.status == "applied").scalar() or 0
    shortlisted = db.query(func.count(Match.id)).filter(Match.status == "shortlisted").scalar() or 0
    selected = db.query(func.count(Match.id)).filter(Match.status == "selected").scalar() or 0
    rejected = db.query(func.count(Match.id)).filter(Match.status == "rejected").scalar() or 0
    
    return {
        "funnel": {
            "total_candidates": total_candidates,
            "total_jobs": total_jobs,
            "total_matches_generated": total_matches,
            "applied": applied,
            "shortlisted": shortlisted,
            "selected": selected,
            "rejected": rejected
        },
        "conversion_rates": {
            "match_to_apply": f"{(applied / total_matches * 100):.1f}%" if total_matches > 0 else "N/A",
            "apply_to_shortlist": f"{(shortlisted / applied * 100):.1f}%" if applied > 0 else "N/A",
            "shortlist_to_select": f"{(selected / shortlisted * 100):.1f}%" if shortlisted > 0 else "N/A"
        }
    }
