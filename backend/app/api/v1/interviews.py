"""
Interview Scheduling API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.interview import Interview
from app.models.application import Application
from app.services.llm_service import LLMService
from app.schemas.features import InterviewCreate, InterviewUpdate, InterviewResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule a new interview"""
    # Verify application exists
    application = db.query(Application).filter(Application.id == data.application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Generate interview questions using LLM
    llm = LLMService()
    from app.models.candidate import Candidate
    from app.models.job import Job
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    questions = None
    if candidate and job:
        cand_skills = []
        if isinstance(candidate.skills, list):
            cand_skills = candidate.skills
        elif isinstance(candidate.skills, dict):
            for sl in candidate.skills.values():
                if isinstance(sl, list):
                    cand_skills.extend(sl)
        
        questions = llm.generate_interview_questions(
            cand_skills[:10],
            job.required_skills or [],
            job.title
        )
    
    interview = Interview(
        application_id=data.application_id,
        recruiter_id=current_user.id,
        candidate_id=data.candidate_id,
        scheduled_at=data.scheduled_at,
        duration_minutes=data.duration_minutes,
        interview_type=data.interview_type,
        location_or_link=data.location_or_link,
        questions_json=questions
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return InterviewResponse.model_validate(interview)


@router.get("/my", response_model=List[InterviewResponse])
async def list_my_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List interviews for current user (as recruiter or candidate)"""
    from app.models.candidate import Candidate
    
    # Check if user is a recruiter
    recruiter_interviews = db.query(Interview).filter(
        Interview.recruiter_id == current_user.id
    ).order_by(Interview.scheduled_at.desc()).all()
    
    # Also check if user is a candidate
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    candidate_interviews = []
    if candidate:
        candidate_interviews = db.query(Interview).filter(
            Interview.candidate_id == candidate.id
        ).order_by(Interview.scheduled_at.desc()).all()
    
    all_interviews = list({i.id: i for i in recruiter_interviews + candidate_interviews}.values())
    return [InterviewResponse.model_validate(i) for i in all_interviews]


@router.patch("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    data: InterviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an interview (reschedule, add notes, change status)"""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Only recruiter or related candidate can update
    if interview.recruiter_id != current_user.id:
        from app.models.candidate import Candidate
        candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
        if not candidate or candidate.id != interview.candidate_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this interview")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(interview, key, value)
    
    db.commit()
    db.refresh(interview)
    
    return InterviewResponse.model_validate(interview)
