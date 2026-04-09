"""
Career Intelligence API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.intelligence_service import IntelligenceService
from app.schemas.intelligence import (
    ProfileCompleteness, SkillGapResponse, CareerSuggestionResponse
)
from app.models.intelligence import CareerSuggestion

router = APIRouter()

@router.get("/completeness", response_model=ProfileCompleteness)
async def get_profile_completeness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weighted profile completeness for the current user"""
    service = IntelligenceService(db)
    return service.calculate_profile_completeness(current_user.id)

@router.get("/gaps/{job_id}", response_model=SkillGapResponse)
async def get_skill_gaps(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze skill gaps between current user and a target job"""
    service = IntelligenceService(db)
    try:
        return service.analyze_skill_gaps(current_user.id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/suggestions", response_model=List[CareerSuggestionResponse])
async def get_career_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized career improvement suggestions"""
    service = IntelligenceService(db)
    # Trigger generation
    await service.generate_career_suggestions(current_user.id)
    
    # Fetch from DB
    suggestions = db.query(CareerSuggestion).filter(
        CareerSuggestion.user_id == current_user.id,
        CareerSuggestion.is_completed == False
    ).order_by(CareerSuggestion.created_at.desc()).all()
    
    return suggestions

@router.post("/suggestions/{suggestion_id}/complete", response_model=dict)
async def complete_suggestion(
    suggestion_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a career suggestion as completed"""
    suggestion = db.query(CareerSuggestion).filter(
        CareerSuggestion.id == suggestion_id,
        CareerSuggestion.user_id == current_user.id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
        
    suggestion.is_completed = True
    db.commit()
    
    return {"message": "Suggestion marked as completed"}
