"""
Match API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from loguru import logger
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime
from app.core.database import get_db, SessionLocal
from app.core.dependencies import get_current_user
from app.models.match import Match
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.user import User, UserRole
from app.models.application import Application
from app.models.notification import Notification
from app.core.socket_manager import manager
from app.schemas.match import MatchResponse, MatchWithDetails
from app.services.matching_engine import MatchingEngine
from app.services.llm_service import LLMService
from app.services.intelligence_service import IntelligenceService

router = APIRouter()
matching_engine = MatchingEngine()
llm_service = LLMService()

def flatten_skills(raw_skills) -> list:
    """Safely flatten candidate skills from any storage format (dict, list, JSON string, or None)."""
    if not raw_skills:
        return []
    # If stored as a JSON-encoded string (double-serialized), parse it first
    if isinstance(raw_skills, str):
        try:
            raw_skills = json.loads(raw_skills)
        except (json.JSONDecodeError, ValueError):
            return []
    # If it's a dict of category -> list (categorized skills)
    if isinstance(raw_skills, dict):
        flat = []
        for skills_list in raw_skills.values():
            if isinstance(skills_list, list):
                flat.extend([s for s in skills_list if s])
        return flat
    # If it's already a flat list
    if isinstance(raw_skills, list):
        return [s for s in raw_skills if s]
    return []

def ensure_match_explanation(match: Match, db: Session) -> str:
    """Helper to ensure a match has an AI explanation (lazy generation)"""
    if match.match_explanation:
        return match.match_explanation
        
    try:
        candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
        job = db.query(Job).filter(Job.id == match.job_id).first()
        
        if not candidate or not job:
            return "Analysis unavailable: Profile or Job not found."
            
        candidate_data = {
            "embedding": candidate.resume_embedding,
            "skills": candidate.skills or {},
            "experience_years": candidate.experience_years or 0
        }
        
        job_data = {
            "embedding": job.job_embedding,
            "required_skills": job.required_skills or [],
            "experience_required": job.experience_required or 0,
            "title": job.title
        }
        
        match_scores = {
            "semantic_similarity": match.semantic_similarity,
            "skill_overlap_score": match.skill_overlap_score,
            "experience_alignment": match.experience_alignment,
            "overall_score": match.overall_score
        }
        
        explanation = llm_service.generate_match_explanation(
            candidate_data, job_data, match_scores
        )
        
        match.match_explanation = explanation
        db.commit()
        return explanation
    except Exception as e:
        logger.error(f"Error generating lazy match explanation for {match.id}: {e}")
        return "AI analysis is temporarily unavailable for this match."

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    candidate_id: str = Query(..., description="Candidate ID"),
    job_id: str = Query(..., description="Job ID"),
    db: Session = Depends(get_db)
):
    """Create a match between candidate and job"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not candidate.resume_embedding or not job.job_embedding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate or job embeddings not available. Please process resume/job first."
        )
    
    # Prepare data for matching
    candidate_data = {
        "embedding": candidate.resume_embedding,
        "skills": candidate.skills or [],
        "experience_years": candidate.experience_years or 0
    }
    
    job_data = {
        "embedding": job.job_embedding,
        "required_skills": job.required_skills or [],
        "experience_required": job.experience_required or 0,
        "title": job.title
    }
    
    # Calculate match scores
    match_scores = matching_engine.match_candidate_to_job(candidate_data, job_data)
    
    # Generate explanation
    explanation = llm_service.generate_match_explanation(
        candidate_data, job_data, match_scores
    )
    
    # Create match record
    db_match = Match(
        candidate_id=candidate_id,
        job_id=job_id,
        semantic_similarity=match_scores["semantic_similarity"],
        skill_overlap_score=match_scores["skill_overlap_score"],
        experience_alignment=match_scores["experience_alignment"],
        overall_score=match_scores["overall_score"],
        match_explanation=explanation
    )
    
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@router.get("/selection-stats")
def get_candidate_selection_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return match/selection stats for the logged-in candidate."""
    # Find the candidate record linked to this user account
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if not candidate:
        return {
            "total_matches": 0,
            "total_applied": 0,
            "shortlisted": 0,
            "selected": 0,
            "recent_activity": []
        }

    # All matches for this candidate
    all_matches = db.query(Match).filter(Match.candidate_id == candidate.id).all()

    # Count by status
    status_counts = {}
    for m in all_matches:
        status_counts[m.status] = status_counts.get(m.status, 0) + 1

    # Build recent activity list (last 10, most recent first)
    recent = sorted(all_matches, key=lambda m: m.created_at, reverse=True)[:10]
    activity = []
    for m in recent:
        job = db.query(Job).filter(Job.id == m.job_id).first()
        activity.append({
            "match_id": m.id,
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "Unknown",
            "match_score": round(m.overall_score * 100, 1),
            "status": m.status,
            "date": m.created_at.strftime("%b %d, %Y") if m.created_at else ""
        })

    return {
        "total_matches": len(all_matches),
        "total_applied": status_counts.get("applied", 0),
        "shortlisted": status_counts.get("shortlisted", 0),
        "selected": status_counts.get("selected", 0),
        "recent_activity": activity
    }

@router.get("/my-matches", response_model=List[MatchWithDetails])

async def get_my_matches(
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum match score filter"),
    max_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum match score filter"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    sort_by: Optional[str] = Query("score", description="Sort by: score, date, salary"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get matches for the currently authenticated user (job seeker)"""
    
    # Ensure user is a job seeker
    if current_user.role != UserRole.JOB_SEEKER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for job seekers"
        )
    
    # Get candidate profile for the user
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found. Please create your profile first."
        )
    
    # Build query
    query = db.query(Match).filter(Match.candidate_id == candidate.id)
    
    # Apply filters
    if min_score is not None:
        query = query.filter(Match.overall_score >= min_score)
    if max_score is not None:
        query = query.filter(Match.overall_score <= max_score)
    
    # Apply sorting
    if sort_by == "score":
        query = query.order_by(Match.overall_score.desc())
    elif sort_by == "date":
        query = query.order_by(Match.created_at.desc())
    else:
        query = query.order_by(Match.overall_score.desc())
    
    # Get matches with pagination
    matches = query.offset(offset).limit(limit).all()
    
    # Build detailed response
    result = []
    for match in matches:
        job = db.query(Job).filter(Job.id == match.job_id).first()
        
        if not job:
            continue
        
        # Apply additional filters
        if job_type and job.job_type != job_type:
            continue
        if location and location.lower() not in (job.location or "").lower():
            continue
        
        # Fallback to User.phone if candidate.phone is missing
        candidate_phone = candidate.phone
        candidate_user_id = None
        user = db.query(User).filter(User.email == candidate.email).first()
        if user:
            candidate_user_id = user.id
            if not candidate_phone:
                candidate_phone = user.phone

        # Flatten candidate skills safely (handles dict, list, JSON string, or None)
        c_skills = flatten_skills(candidate.skills)

        # Populate Intelligence (graceful degradation)
        try:
            intelligence = IntelligenceService(db, llm_service).get_match_intelligence(match.id)
        except Exception as intel_err:
            logger.warning(f"Intelligence computation failed for match {match.id}: {intel_err}")
            intelligence = None

        # Recruiter contact info for the candidate
        recruiter_name, recruiter_email, recruiter_phone = None, None, None
        if job.recruiter_id:
            recruiter_user = db.query(User).filter(User.id == job.recruiter_id).first()
            if recruiter_user:
                recruiter_name = recruiter_user.full_name
                recruiter_email = recruiter_user.email
                recruiter_phone = recruiter_user.phone

        # Get application for cover letter
        application = db.query(Application).filter(Application.match_id == match.id).first()
        cover_letter = application.cover_letter if application else None

        match_dict = {
            "id": match.id,
            "status": match.status,
            **{k: v for k, v in match.__dict__.items() if not k.startswith('_')},
            "candidate_name": candidate.name,
            "candidate_email": candidate.email,
            "candidate_phone": candidate_phone,
            "candidate_resume_path": candidate.resume_file_path,
            "candidate_resume_summary": candidate.resume_summary,
            "candidate_skills": c_skills,
            "job_title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "experience_required": job.experience_required,
            "education_required": job.education_required,
            "intelligence": intelligence,
            "cover_letter": cover_letter,
            "recruiter_name": recruiter_name,
            "recruiter_email": recruiter_email,
            "recruiter_phone": recruiter_phone,
            "candidate_user_id": candidate_user_id
        }
        result.append(match_dict)
    
    return result

@router.get("/{match_id}", response_model=MatchWithDetails)
async def get_match_details(
    match_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific match (lazy generates AI explanation)"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    job = db.query(Job).filter(Job.id == match.job_id).first()
    candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
    
    if not job or not candidate:
        raise HTTPException(status_code=404, detail="Associated job or candidate not found")

    # Lazy generate explanation if missing
    ensure_match_explanation(match, db)
    
    candidate_phone = candidate.phone
    candidate_user_id = None
    user = db.query(User).filter(User.email == candidate.email).first()
    if user:
        candidate_user_id = user.id
        if not candidate_phone:
            candidate_phone = user.phone

    c_skills = flatten_skills(candidate.skills)

    # Populate Intelligence (graceful degradation)
    try:
        intelligence = IntelligenceService(db, llm_service).get_match_intelligence(match.id)
    except Exception as intel_err:
        logger.warning(f"Intelligence computation failed for match {match.id}: {intel_err}")
        intelligence = None

    # Recruiter contact info for the candidate
    recruiter_name, recruiter_email, recruiter_phone = None, None, None
    if job.recruiter_id:
        recruiter_user = db.query(User).filter(User.id == job.recruiter_id).first()
        if recruiter_user:
            recruiter_name = recruiter_user.full_name
            recruiter_email = recruiter_user.email
            recruiter_phone = recruiter_user.phone

    # Get application for cover letter
    application = db.query(Application).filter(Application.match_id == match.id).first()
    cover_letter = application.cover_letter if application else None

    return {
        "id": match.id,
        "status": match.status,
        **{k: v for k, v in match.__dict__.items() if not k.startswith('_')},
        "candidate_name": candidate.name,
        "candidate_email": candidate.email,
        "candidate_phone": candidate_phone,
        "candidate_resume_path": candidate.resume_file_path,
        "candidate_resume_summary": candidate.resume_summary,
        "candidate_skills": c_skills,
        "job_title": job.title,
        "company": job.company,
        "location": job.location,
        "job_type": job.job_type,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "description": job.description,
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "experience_required": job.experience_required,
        "education_required": job.education_required,
        "intelligence": intelligence,
        "cover_letter": cover_letter,
        "recruiter_name": recruiter_name,
        "recruiter_email": recruiter_email,
        "recruiter_phone": recruiter_phone,
        "candidate_user_id": candidate_user_id
    }

@router.get("/candidate/{candidate_id}", response_model=List[MatchWithDetails])
async def get_candidate_matches(
    candidate_id: str,
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum match score filter"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all matches for a candidate, sorted by score"""
    query = db.query(Match).filter(Match.candidate_id == candidate_id)
    
    if min_score is not None:
        query = query.filter(Match.overall_score >= min_score)
    
    matches = query.order_by(Match.overall_score.desc()).limit(limit).all()
    
    result = []
    for match in matches:
        job = db.query(Job).filter(Job.id == match.job_id).first()
        candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
        
        if not job or not candidate:
            continue
            
        # Fallback to User.phone if candidate.phone is missing
        candidate_phone = candidate.phone
        candidate_user_id = None
        user = db.query(User).filter(User.email == candidate.email).first()
        if user:
            candidate_user_id = user.id
            if not candidate_phone:
                candidate_phone = user.phone

        # Flatten candidate skills safely (handles dict, list, JSON string, or None)
        c_skills = flatten_skills(candidate.skills)

        # Recruiter contact info for the candidate
        recruiter_name, recruiter_email, recruiter_phone = None, None, None
        if job.recruiter_id:
            recruiter_user = db.query(User).filter(User.id == job.recruiter_id).first()
            if recruiter_user:
                recruiter_name = recruiter_user.full_name
                recruiter_email = recruiter_user.email
                recruiter_phone = recruiter_user.phone

        # Populate Intelligence (graceful degradation)
        try:
            _intelligence = IntelligenceService(db, llm_service).get_match_intelligence(match.id)
        except Exception as intel_err:
            logger.warning(f"Intelligence failed for match {match.id}: {intel_err}")
            _intelligence = None

        match_dict = {
            "id": match.id,
            "status": match.status,
            **{k: v for k, v in match.__dict__.items() if not k.startswith('_')},
            "candidate_name": candidate.name,
            "candidate_email": candidate.email,
            "candidate_phone": candidate_phone,
            "candidate_resume_path": candidate.resume_file_path,
            "candidate_resume_summary": candidate.resume_summary,
            "candidate_skills": c_skills,
            "job_title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "experience_required": job.experience_required,
            "education_required": job.education_required,
            "intelligence": _intelligence,
            "cover_letter": db.query(Application).filter(Application.match_id == match.id).first().cover_letter if db.query(Application).filter(Application.match_id == match.id).first() else None,
            "candidate_user_id": candidate_user_id,
            "recruiter_id": job.recruiter_id,
            "recruiter_name": recruiter_name,
            "recruiter_email": recruiter_email,
            "recruiter_phone": recruiter_phone
        }
        result.append(match_dict)
    
    return result

@router.get("/recruiter-matches", response_model=List[MatchWithDetails])
async def get_all_recruiter_matches(
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all matches for all jobs posted by the recruiter"""
    if current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters and admins can access this endpoint"
        )
    
    # Get all job IDs for this recruiter
    job_query = db.query(Job.id)
    if current_user.role == UserRole.RECRUITER.value:
        job_query = job_query.filter(Job.recruiter_id == current_user.id)
    
    job_ids = [r[0] for r in job_query.all()]
    
    if not job_ids:
        return []
    
    # Get matches for these jobs
    query = db.query(Match).filter(Match.job_id.in_(job_ids))
    
    if min_score is not None:
        query = query.filter(Match.overall_score >= min_score)
    if max_score is not None:
        query = query.filter(Match.overall_score <= max_score)
    
    matches = query.order_by(Match.overall_score.desc()).limit(limit).all()
    
    result = []
    for match in matches:
        job = db.query(Job).filter(Job.id == match.job_id).first()
        candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
        
        if not job or not candidate:
            continue
            
        # candidate_phone = candidate.phone or (db.query(User).filter(User.email == candidate.email).first().phone if db.query(User).filter(User.email == candidate.email).first() else None)
        candidate_phone = candidate.phone
        candidate_user_id = None
        user = db.query(User).filter(User.email == candidate.email).first()
        if user:
            candidate_user_id = user.id
            if not candidate_phone:
                candidate_phone = user.phone

        # Flatten candidate skills safely (handles dict, list, JSON string, or None)
        c_skills = flatten_skills(candidate.skills)

        # Recruiter contact info for the candidate
        recruiter_name, recruiter_email, recruiter_phone = None, None, None
        if job.recruiter_id:
            recruiter_user = db.query(User).filter(User.id == job.recruiter_id).first()
            if recruiter_user:
                recruiter_name = recruiter_user.full_name
                recruiter_email = recruiter_user.email
                recruiter_phone = recruiter_user.phone

        # Populate Intelligence (graceful degradation)
        try:
            _intelligence = IntelligenceService(db, llm_service).get_match_intelligence(match.id)
        except Exception as intel_err:
            logger.warning(f"Intelligence failed for match {match.id}: {intel_err}")
            _intelligence = None

        match_dict = {
            "id": match.id,
            "status": match.status,
            **{k: v for k, v in match.__dict__.items() if not k.startswith('_')},
            "candidate_name": candidate.name,
            "candidate_email": candidate.email,
            "candidate_phone": candidate_phone,
            "candidate_resume_path": candidate.resume_file_path,
            "candidate_resume_summary": candidate.resume_summary,
            "candidate_skills": c_skills,
            "job_title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "experience_required": job.experience_required,
            "education_required": job.education_required,
            "intelligence": _intelligence,
            "cover_letter": db.query(Application).filter(Application.match_id == match.id).first().cover_letter if db.query(Application).filter(Application.match_id == match.id).first() else None,
            "candidate_user_id": candidate_user_id,
            "recruiter_id": job.recruiter_id,
            "recruiter_name": recruiter_name,
            "recruiter_email": recruiter_email,
            "recruiter_phone": recruiter_phone
        }
        result.append(match_dict)
    
    return result

@router.get("/job/{job_id}", response_model=List[MatchWithDetails])
async def get_job_matches(
    job_id: str,
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum match score filter"),
    max_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum match score filter"),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all matches for a job, sorted by score (secured)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Security check: Recruiter must own the job, or be an admin
    if current_user.role == UserRole.RECRUITER.value and job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to matches for this job"
        )
    
    query = db.query(Match).filter(Match.job_id == job_id)
    
    if min_score is not None:
        query = query.filter(Match.overall_score >= min_score)
    if max_score is not None:
        query = query.filter(Match.overall_score <= max_score)
    
    matches = query.order_by(Match.overall_score.desc()).limit(limit).all()
    
    result = []
    for match in matches:
        candidate = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
        if not candidate: continue
            
        # candidate_phone = candidate.phone or (db.query(User).filter(User.email == candidate.email).first().phone if db.query(User).filter(User.email == candidate.email).first() else None)
        candidate_phone = candidate.phone
        candidate_user_id = None
        user = db.query(User).filter(User.email == candidate.email).first()
        if user:
            candidate_user_id = user.id
            if not candidate_phone:
                candidate_phone = user.phone

        # Get application for cover letter
        application = db.query(Application).filter(Application.match_id == match.id).first()
        cover_letter = application.cover_letter if application else None

        # Flatten candidate skills safely
        c_skills = flatten_skills(candidate.skills)

        # Populate Intelligence (graceful degradation)
        try:
            _intelligence = IntelligenceService(db, llm_service).get_match_intelligence(match.id)
        except Exception as intel_err:
            logger.warning(f"Intelligence failed for match {match.id}: {intel_err}")
            _intelligence = None

        result.append({
            "id": match.id,
            "status": match.status,
            **{k: v for k, v in match.__dict__.items() if not k.startswith('_')},
            "candidate_name": candidate.name,
            "candidate_email": candidate.email,
            "candidate_phone": candidate_phone,
            "candidate_resume_path": candidate.resume_file_path,
            "candidate_resume_summary": candidate.resume_summary,
            "candidate_skills": c_skills,
            "job_title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "experience_required": job.experience_required,
            "education_required": job.education_required,
            "intelligence": _intelligence,
            "cover_letter": cover_letter,
            "candidate_user_id": candidate_user_id
        })
    
    return result



@router.post("/generate-for-candidate/{candidate_id}", status_code=status.HTTP_202_ACCEPTED)
def generate_matches_for_candidate(
    candidate_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate matches for a candidate against all active jobs (Background Task)"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.resume_embedding:
        raise HTTPException(
            status_code=400, 
            detail="Candidate resume not processed. Please upload and process resume first."
        )
    
    # Use the same optimized task function defined in candidates.py or similar
    # For simplicity and to avoid circular imports, we can define a shared utility or just reuse the logic.
    # Actually, I'll import it from candidates if possible, or just define a local version.
    
    from app.api.v1.candidates import generate_matches_task
    background_tasks.add_task(generate_matches_task, candidate.id)
    
    return {
        "message": "Match generation started in the background. Please refresh in a few moments.",
        "candidate_id": candidate_id
    }

@router.post("/{match_id}/apply", response_model=MatchResponse)
def apply_to_job(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update match status to 'applied' (simple, no cover letter)"""
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only job seekers can apply to jobs")

    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if not candidate or match.candidate_id != candidate.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this match")

    match.status = "applied"
    db.commit()
    db.refresh(match)
    return match


from pydantic import BaseModel as PydanticBaseModel

class ApplyWithFormRequest(PydanticBaseModel):
    cover_letter: str = ""


@router.post("/{match_id}/apply-with-form")
async def apply_to_job_with_form(
    match_id: str,
    body: ApplyWithFormRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply to a job with an optional cover letter. Fires email + SMS to recruiter."""
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only job seekers can apply to jobs")

    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if not candidate or match.candidate_id != candidate.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this match")

    # 1. Update match status
    match.status = "applied"

    # 2. Create Application record (upsert — allow re-submitting)
    existing_app = db.query(Application).filter(Application.match_id == match_id).first()
    if existing_app:
        existing_app.cover_letter = body.cover_letter
    else:
        db.add(Application(
            match_id=match_id,
            candidate_id=candidate.id,
            job_id=match.job_id,
            cover_letter=body.cover_letter
        ))

    # 3. Create in-app Notification for the recruiter
    job = db.query(Job).filter(Job.id == match.job_id).first()
    recruiter_user = None
    if job and job.recruiter_id:
        recruiter_user = db.query(User).filter(User.id == job.recruiter_id).first()
        if recruiter_user:
            db.add(Notification(
                user_id=recruiter_user.id,
                type="application_received",
                message=f"{candidate.name} applied to your '{job.title}' position at {job.company}.",
                related_match_id=match_id
            ))
            
            # Real-time update via WebSocket
            try:
                await manager.send_json_to_user({
                    "type": "new_notification",
                    "notification": {
                        "type": "application_received",
                        "message": f"{candidate.name} applied to your '{job.title}' position.",
                        "related_match_id": match_id,
                        "created_at": datetime.utcnow().isoformat()
                    }
                }, recruiter_user.id)
            except Exception as ws_err:
                logger.error(f"Failed to send real-time notification: {ws_err}")

    db.commit()

    # 4. Fire email + SMS in background so response is instant
    if recruiter_user and job:
        from app.services.notification_service import NotificationService
        notif_service = NotificationService()
        recruiter_phone = getattr(recruiter_user, "phone", "") or ""
        background_tasks.add_task(
            notif_service.notify_recruiter_of_application,
            recruiter_email=recruiter_user.email,
            recruiter_phone=recruiter_phone,
            recruiter_name=recruiter_user.full_name or recruiter_user.email,
            candidate_name=candidate.name,
            job_title=job.title,
            company=job.company,
            cover_letter=body.cover_letter
        )
        
        # Candidate notification
        background_tasks.add_task(
            notif_service.notify_candidate_of_application,
            candidate_email=candidate.email,
            candidate_name=candidate.name,
            job_title=job.title,
            company=job.company
        )

    return {"message": "Application submitted successfully!", "match_id": match_id, "status": "applied"}


@router.post("/generate-for-me", status_code=status.HTTP_202_ACCEPTED)
def generate_matches_for_me(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate matches for the current authenticated user against all active jobs"""
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can generate matches"
        )
    
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found. Please upload a resume first."
        )
    
    return generate_matches_for_candidate(candidate_id=candidate.id, background_tasks=background_tasks, db=db)

@router.patch("/{match_id}/status", response_model=MatchResponse)
def update_match_status(
    match_id: str,
    status: str = Query(..., pattern="^(matched|applied|screened|interview|offered|hired|rejected)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update match status (Recruiter only)"""
    if current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only recruiters can update match status")
    
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    match.status = status
    db.commit()
    db.refresh(match)
    return match


def generate_matches_for_job_task(job_id: str):
    """Background task to generate matches for a specific job against all candidates"""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or not job.job_embedding:
            return

        # Prepare job data
        job_data = {
            "embedding": job.job_embedding,
            "required_skills": job.required_skills or [],
            "experience_required": job.experience_required or 0,
            "title": job.title,
            "skills_by_category": job.skills_by_category or {}
        }
        
        # Get all candidates with embeddings
        candidates = db.query(Candidate).filter(Candidate.resume_embedding.isnot(None)).all()
        
        matching_engine = MatchingEngine()
        
        for candidate in candidates:
            # Check if match exists (skip if exists)
            existing_match = db.query(Match).filter(
                Match.candidate_id == candidate.id,
                Match.job_id == job.id
            ).first()
            
            if existing_match:
                continue

            # Prepare candidate data
            candidate_data = {
                "embedding": candidate.resume_embedding,
                "skills": candidate.skills or [],
                "experience_years": candidate.experience_years or 0
            }
            
            # Calculate match
            scores = matching_engine.match_candidate_to_job(candidate_data, job_data)
            
            # Create match if score > threshold (e.g. 0.1 to be inclusive)
            if scores['overall_score'] >= 0.1:
                match = Match(
                    candidate_id=candidate.id,
                    job_id=job.id,
                    semantic_similarity=scores['semantic_similarity'],
                    skill_overlap_score=scores['skill_overlap_score'],
                    experience_alignment=scores['experience_alignment'],
                    overall_score=scores['overall_score'],
                    status='matched'
                )
                db.add(match)
        
        db.commit()
    except Exception as e:
        logger.error(f"Error generating matches for job {job_id}: {e}")
    finally:
        db.close()

@router.post("/generate-for-recruiter", status_code=status.HTTP_202_ACCEPTED)
def generate_matches_for_recruiter(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate matches for all jobs posted by the current recruiter"""
    if current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only recruiters can generate matches")
    
    # Get recruiter's jobs
    jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
    
    if not jobs:
        return {"message": "No jobs found for this recruiter"}
        
    for job in jobs:
        background_tasks.add_task(generate_matches_for_job_task, job.id)
        
    return {"message": f"Started match generation for {len(jobs)} jobs"}

