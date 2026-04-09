"""
Job API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.models.job import Job
from app.models.user import User, UserRole
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services.nlp_processor import NLPProcessor
from app.services.llm_service import LLMService
from app.core.config import settings

router = APIRouter()

# Lazy-load these services
_nlp_processor = None
_llm_service = None

def get_nlp_processor():
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = NLPProcessor(
            spacy_model=settings.SPACY_MODEL,
            embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
        )
    return _nlp_processor

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job: JobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting"""
    db_job = Job(**job.dict())
    db_job.recruiter_id = current_user.id
    
    # Generate embedding for job description
    nlp_processor = get_nlp_processor()
    llm_service = get_llm_service()
    
    embedding = nlp_processor.generate_embedding(job.description)
    db_job.job_embedding = embedding
    
    # Normalize job title using LLM
    normalized_title = llm_service.normalize_job_title(job.title)
    db_job.normalized_title = normalized_title
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Trigger background matching task so matches appear instantly for the recruiter
    from app.api.v1.matches import generate_matches_for_job_task
    background_tasks.add_task(generate_matches_for_job_task, db_job.id)
    
    return db_job

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get jobs (filtered for recruiters if logged in)"""
    query = db.query(Job)
    
    # Check if a user is logged in as recruiter
    if current_user and current_user.role == "recruiter":
        query = query.filter(Job.recruiter_id == current_user.id)
        
    if active_only:
        query = query.filter(Job.is_active == True)
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: str,
    job_update: JobUpdate,
    db: Session = Depends(get_db)
):
    """Update a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    update_data = job_update.dict(exclude_unset=True)
    
    # Regenerate embedding if description changed
    if "description" in update_data:
        nlp_processor = get_nlp_processor()
        embedding = nlp_processor.generate_embedding(update_data["description"])
        job.job_embedding = embedding
    
    for field, value in update_data.items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job posting (only by owner or admin)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Ownership check
    if job.recruiter_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this job"
        )
    
    db.delete(job)
    db.commit()
    return None
