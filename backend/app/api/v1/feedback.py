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
    Filtered by recruiter roles for individual recruiters.
    """
    # Skill demand is more useful as a MARKET insight
    # So we show platform-wide skill demand, but can highlight recruiter's own data if needed
    query = db.query(Job).filter(Job.is_active == True)
    
    # We always show global for "Skill Demand" to provide market intelligence
    # But we can still count the recruiter's jobs separately
    recruiter_jobs_count = 0
    if current_user.role == "recruiter":
        recruiter_jobs_count = db.query(Job).filter(
            Job.is_active == True, 
            Job.recruiter_id == current_user.id
        ).count()
        
    jobs = query.all()
    
    skill_counts = {}
    for job in jobs:
        skills = job.required_skills or []
        for skill in skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Sort by count descending
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        "top_skills": [{"skill": s, "demand_count": c} for s, c in sorted_skills],
        "total_active_jobs": recruiter_jobs_count if current_user.role == "recruiter" else len(jobs),
        "platform_active_jobs": len(jobs)
    }

@router.get("/analytics/match-quality")
async def get_match_quality_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregate statistics on match quality and feedback.
    """
    query = db.query(Match)
    
    # For match quality, we also want to show platform-wide stats as a benchmark
    total_platform_matches = db.query(Match).count()
    
    # If recruiter, we'll focus on their matches but provide platform data too
    if current_user.role == "recruiter":
        recruiter_query = query.join(Job).filter(Job.recruiter_id == current_user.id)
        total_recruiter_matches = recruiter_query.count()
        
        # If the recruiter has NO matches yet, show platform stats so they see something
        if total_recruiter_matches == 0:
            query = query # Use global query
        else:
            query = recruiter_query
    
    total_matches = query.count()
    
    # Score distribution
    excellent = query.filter(Match.overall_score >= 0.8).count()
    good = query.filter(
        and_(Match.overall_score >= 0.6, Match.overall_score < 0.8)
    ).count()
    fair = query.filter(
        and_(Match.overall_score >= 0.4, Match.overall_score < 0.6)
    ).count()
    low = query.filter(Match.overall_score < 0.4).count()
    
    # Average scores
    avg_overall = db.query(func.avg(Match.overall_score))
    avg_semantic = db.query(func.avg(Match.semantic_similarity))
    avg_skill = db.query(func.avg(Match.skill_overlap_score))
    
    if current_user.role == "recruiter":
        avg_overall = avg_overall.join(Job).filter(Job.recruiter_id == current_user.id)
        avg_semantic = avg_semantic.join(Job).filter(Job.recruiter_id == current_user.id)
        avg_skill = avg_skill.join(Job).filter(Job.recruiter_id == current_user.id)
        
    avg_overall = avg_overall.scalar() or 0
    avg_semantic = avg_semantic.scalar() or 0
    avg_skill = avg_skill.scalar() or 0
    
    return {
        "total_matches": total_matches,
        "total_platform_matches": total_platform_matches,
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
    # Base queries
    match_query = db.query(Match)
    job_query = db.query(Job)
    candidate_query = db.query(Candidate)
    
    # Total candidates is ALWAYS platform-wide for market intelligence
    # but we can also count those specifically matched to the recruiter
    total_candidates_platform = db.query(Candidate).count()
    
    if current_user.role == "recruiter":
        # Recruiters only see their jobs and matches for those jobs
        job_query = job_query.filter(Job.recruiter_id == current_user.id)
        match_query = match_query.join(Job).filter(Job.recruiter_id == current_user.id)
        
        # Recruiter-specific candidate pool
        recruiter_candidate_count = candidate_query.join(Match).join(Job).filter(Job.recruiter_id == current_user.id).distinct().count()
    else:
        recruiter_candidate_count = total_candidates_platform

    total_candidates = total_candidates_platform # Always show global pool
    total_jobs = job_query.count()
    total_matches = match_query.count()
    
    # Detailed funnel stages
    applied = match_query.filter(Match.status == "applied").count()
    screened = match_query.filter(Match.status == "screened").count()
    interview = match_query.filter(Match.status == "interview").count()
    offered = match_query.filter(Match.status == "offered").count()
    hired = match_query.filter(Match.status == "hired").count()
    rejected = match_query.filter(Match.status == "rejected").count()
    selected = match_query.filter(Match.status == "selected").count()
    
    return {
        "funnel": {
            "total_candidates": total_candidates,
            "total_jobs": total_jobs,
            "total_matches_generated": total_matches,
            "applied": applied,
            "screened": screened,
            "interview": interview,
            "offered": offered,
            "hired": hired + selected,
            "rejected": rejected
        },
        "conversion_rates": {
            "match_to_apply": f"{(applied / total_matches * 100):.1f}%" if total_matches > 0 else "N/A",
            "apply_to_interview": f"{(interview / applied * 100):.1f}%" if applied > 0 else "N/A",
            "interview_to_hire": f"{( (hired + selected) / interview * 100):.1f}%" if interview > 0 else "N/A"
        }
    }
