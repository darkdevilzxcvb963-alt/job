"""
Shortlists API - recruiter candidate management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.shortlist import Shortlist, ShortlistCandidate
from app.models.candidate import Candidate
from app.schemas.features import ShortlistCreate, ShortlistAddCandidate, ShortlistResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=ShortlistResponse, status_code=status.HTTP_201_CREATED)
async def create_shortlist(
    data: ShortlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new shortlist"""
    shortlist = Shortlist(
        recruiter_id=current_user.id,
        name=data.name,
        job_id=data.job_id
    )
    db.add(shortlist)
    db.commit()
    db.refresh(shortlist)
    
    return ShortlistResponse(
        id=shortlist.id,
        recruiter_id=shortlist.recruiter_id,
        name=shortlist.name,
        job_id=shortlist.job_id,
        candidate_count=0,
        created_at=shortlist.created_at
    )


@router.get("/", response_model=List[ShortlistResponse])
async def list_shortlists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all shortlists for current recruiter"""
    shortlists = db.query(Shortlist).filter(
        Shortlist.recruiter_id == current_user.id
    ).order_by(Shortlist.created_at.desc()).all()
    
    results = []
    for sl in shortlists:
        count = db.query(ShortlistCandidate).filter(
            ShortlistCandidate.shortlist_id == sl.id
        ).count()
        results.append(ShortlistResponse(
            id=sl.id,
            recruiter_id=sl.recruiter_id,
            name=sl.name,
            job_id=sl.job_id,
            candidate_count=count,
            created_at=sl.created_at
        ))
    
    return results


@router.post("/{shortlist_id}/candidates", status_code=status.HTTP_201_CREATED)
async def add_candidate_to_shortlist(
    shortlist_id: str,
    data: ShortlistAddCandidate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a candidate to a shortlist"""
    shortlist = db.query(Shortlist).filter(
        Shortlist.id == shortlist_id,
        Shortlist.recruiter_id == current_user.id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="Shortlist not found")
    
    # Check if already added
    existing = db.query(ShortlistCandidate).filter(
        ShortlistCandidate.shortlist_id == shortlist_id,
        ShortlistCandidate.candidate_id == data.candidate_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Candidate already in shortlist")
    
    entry = ShortlistCandidate(
        shortlist_id=shortlist_id,
        candidate_id=data.candidate_id,
        notes=data.notes
    )
    db.add(entry)
    db.commit()
    
    return {"message": "Candidate added to shortlist"}


@router.get("/{shortlist_id}/candidates")
async def get_shortlist_candidates(
    shortlist_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all candidates in a shortlist"""
    shortlist = db.query(Shortlist).filter(
        Shortlist.id == shortlist_id,
        Shortlist.recruiter_id == current_user.id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="Shortlist not found")
    
    entries = db.query(ShortlistCandidate).filter(
        ShortlistCandidate.shortlist_id == shortlist_id
    ).order_by(ShortlistCandidate.added_at.desc()).all()
    
    results = []
    for entry in entries:
        candidate = db.query(Candidate).filter(Candidate.id == entry.candidate_id).first()
        if candidate:
            results.append({
                "id": entry.id,
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "candidate_email": candidate.email,
                "skills": candidate.skills,
                "experience_years": candidate.experience_years,
                "notes": entry.notes,
                "added_at": entry.added_at.isoformat()
            })
    
    return results


@router.delete("/{shortlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shortlist(
    shortlist_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a shortlist"""
    shortlist = db.query(Shortlist).filter(
        Shortlist.id == shortlist_id,
        Shortlist.recruiter_id == current_user.id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="Shortlist not found")
    
    db.delete(shortlist)
    db.commit()


@router.delete("/{shortlist_id}/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_candidate_from_shortlist(
    shortlist_id: str,
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a candidate from a shortlist"""
    entry = db.query(ShortlistCandidate).filter(
        ShortlistCandidate.shortlist_id == shortlist_id,
        ShortlistCandidate.candidate_id == candidate_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Candidate not in shortlist")
    
    db.delete(entry)
    db.commit()
