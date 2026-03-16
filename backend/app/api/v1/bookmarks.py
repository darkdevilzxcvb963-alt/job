"""
Bookmarks API - Save/unsave jobs for candidates
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.saved_job import SavedJob
from app.models.job import Job
from app.schemas.features import SavedJobCreate, SavedJobResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
async def save_job(
    data: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save/bookmark a job"""
    # Check if already saved
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == data.job_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Job already saved")
    
    # Verify job exists
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    saved = SavedJob(
        user_id=current_user.id,
        job_id=data.job_id,
        notes=data.notes
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    
    return SavedJobResponse(
        id=saved.id,
        user_id=saved.user_id,
        job_id=saved.job_id,
        notes=saved.notes,
        created_at=saved.created_at,
        job_title=job.title,
        company=job.company,
        location=job.location
    )


@router.get("/", response_model=List[SavedJobResponse])
async def list_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all saved jobs for current user"""
    saved_jobs = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id
    ).order_by(SavedJob.created_at.desc()).all()
    
    results = []
    for sj in saved_jobs:
        job = db.query(Job).filter(Job.id == sj.job_id).first()
        results.append(SavedJobResponse(
            id=sj.id,
            user_id=sj.user_id,
            job_id=sj.job_id,
            notes=sj.notes,
            created_at=sj.created_at,
            job_title=job.title if job else None,
            company=job.company if job else None,
            location=job.location if job else None
        ))
    
    return results


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a saved job"""
    saved = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")
    
    db.delete(saved)
    db.commit()
