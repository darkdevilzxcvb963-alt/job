from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from loguru import logger

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.schemas.ai_trainer import TrainingResponse
from app.services.ai_trainer_service import AITrainerService
from app.services.intelligence_service import IntelligenceService
import json

router = APIRouter()
ai_trainer_service = AITrainerService()

def flatten_skills(raw_skills) -> list:
    """Safely flatten candidate skills from various storage formats."""
    if not raw_skills:
        return []
    if isinstance(raw_skills, str):
        try:
            raw_skills = json.loads(raw_skills)
        except (json.JSONDecodeError, ValueError):
            return []
    if isinstance(raw_skills, dict):
        flat = []
        for skills_list in raw_skills.values():
            if isinstance(skills_list, list):
                flat.extend([s for s in skills_list if s])
        return flat
    if isinstance(raw_skills, list):
        return [s for s in raw_skills if s]
    return []

@router.post("/generate", response_model=TrainingResponse)
async def generate_training_plan(
    match_id: str = Query(..., description="The ID of the match between candidate and job"),
    question: Optional[str] = Query(None, description="Optional interview question for evaluation"),
    answer: Optional[str] = Query(None, description="Optional candidate answer for evaluation"),
    roadmap_days: Optional[int] = Query(14, description="Preferred duration of roadmap"),
    quiz_type: Optional[str] = Query("Mixed", description="Interview pattern: MCQ, Fill-in-the-Blanks, Big Questions, Mixed"),
    chat_turn: Optional[int] = Query(0, description="The current turn in the chat conversation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an AI-powered training plan, interview questions, and roadmap
    based on a specific match.
    """
    # 1. Fetch match data
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # 2. Security Check: Only the candidate or a recruiter/admin can access
    candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    is_own_profile = (current_user.email == candidate.email)
    is_privileged = (current_user.role in [UserRole.RECRUITER.value, UserRole.ADMIN.value])
    
    if not (is_own_profile or is_privileged):
        raise HTTPException(status_code=403, detail="Not authorized to access this training data")

    # 3. Fetch Job data
    job = db.query(Job).filter(Job.id == match.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Associated job not found")

    # 4. Extract and process skills
    cand_skills_list = flatten_skills(candidate.skills)
    job_skills_list = job.required_skills or []
    
    cand_skills_set = set([s.lower() for s in cand_skills_list])
    job_skills_set = set([s.lower() for s in job_skills_list])
    
    matched_skills = list(cand_skills_set & job_skills_set)
    missing_skills = list(job_skills_set - cand_skills_set)

    # 5. Call Gemini via AITrainerService
    try:
        training_data = await ai_trainer_service.generate_training_plan(
            job_role=job.title,
            candidate_skills=cand_skills_list,
            job_skills=job_skills_list,
            matched_skills=matched_skills,
            question=question,
            answer=answer,
            roadmap_days=roadmap_days,
            quiz_type=quiz_type,
            chat_turn=chat_turn
        )

        # Explicit Pydantic validation before returning — surfaces bad AI output clearly
        from app.schemas.ai_trainer import TrainingResponse as TR
        from pydantic import ValidationError
        try:
            TR(**training_data)
        except ValidationError as ve:
            logger.error(f"Training response failed Pydantic validation: {ve}")
            # Attempt to fix the payload and retry with mock
            training_data = ai_trainer_service._build_mock_payload(
                job.title, missing_skills, roadmap_days
            )

        return training_data

    except Exception as e:
        logger.error(f"Error in training plan generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate training plan: {str(e)}"
        )

@router.post("/generate-questions", response_model=Dict[str, Any])
async def generate_topic_questions(
    topic: str = Query(..., description="The specific skill gap topic"),
    job_role: str = Query(..., description="The target job role"),
    current_user: User = Depends(get_current_user)
):
    """
    On-demand (JIT) generation of 10 questions for a specific topic.
    Used to prevent token exhaustion by only generating what's needed.
    """
    try:
        logger.info(f"JIT Request: {topic} for {job_role}")
        questions = await ai_trainer_service.generate_questions_for_topic(
            topic=topic,
            job_role=job_role,
            count=10
        )
        return {"questions": questions}
    except Exception as e:
        logger.error(f"JIT Generation Error: {e}")
        # Return fallback mock if AI fails
        return {"questions": []}

@router.get("/status", response_model=Dict[str, str])
async def get_service_status():
    """Verify if Gemini API is configured and reachable"""
    try:
        # Check if keys are available
        key_count = len(ai_trainer_service.api_keys)
        if key_count == 0:
            return {"status": "offline", "reason": "No API keys configured"}
        
        # We can't really "ping" Gemini without a request, 
        # but we can return the model being used and key count
        return {
            "status": "online", 
            "model": ai_trainer_service.fallback_models[ai_trainer_service.current_model_index],
            "api_keys_active": str(key_count),
            "current_key_index": str(ai_trainer_service.current_key_index)
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"status": "offline", "reason": str(e)}

