"""
Admin Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from loguru import logger
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole, CandidateProfile, RecruiterProfile
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.schemas.auth import UserResponse, AdminResetPassword, UserDetailResponse


router = APIRouter(tags=["admin"])

# ===================== Admin Verification Helpers =====================

def verify_admin_access(current_user: User):
    """Verify that user has admin role"""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ===================== User Management Endpoints =====================

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: str = Query(None),
    is_verified: bool = Query(None),
    is_active: bool = Query(None),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin or Recruiter)
    Filters: role, is_verified, is_active, search (by email/name)
    """
    if current_user.role not in [UserRole.ADMIN.value, UserRole.RECRUITER.value]:
        raise HTTPException(status_code=403, detail="Access required")
        
    # Recruiters can only search for job seekers
    if current_user.role == UserRole.RECRUITER.value:
        role = UserRole.JOB_SEEKER.value
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_details(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user information including profile and resume (admin only)"""
    verify_admin_access(current_user)
    
    # query user with profile relationships loaded? 
    # default relationship loading should handle it if accessed
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Manual construction to include resume data from Candidate model
    # Link Candidate by email
    candidate_resume = db.query(Candidate).filter(Candidate.email == user.email).first()
    
    # Construct response
    response = UserDetailResponse.from_orm(user)
    
    if candidate_resume:
        response.resume_data = candidate_resume
    
    return response

@router.post("/users/{user_id}/verify")
async def verify_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually verify a user (admin only)"""
    verify_admin_access(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return {"message": "User is already verified"}
    
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    
    logger.info(f"Admin {current_user.email} verified user {user.email}")
    return {"message": "User verified successfully"}

@router.post("/users/{user_id}/reject")
async def reject_user(
    user_id: str,
    reason: str = Query(..., min_length=1, max_length=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject/deactivate a user (admin only)"""
    verify_admin_access(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    logger.info(f"Admin {current_user.email} rejected user {user.email}. Reason: {reason}")
    return {"message": f"User deactivated. Reason: {reason}"}

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate a deactivated user (admin only)"""
    verify_admin_access(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    logger.info(f"Admin {current_user.email} reactivated user {user.email}")
    return {"message": "User activated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently delete a user (admin only)"""
    verify_admin_access(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_email = user.email
    db.delete(user)
    db.commit()
    
    logger.info(f"Admin {current_user.email} deleted user {user_email}")
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/reset-password")
async def admin_reset_user_password(
    user_id: str,
    reset_data: AdminResetPassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset a user's password directly (admin only)"""
    verify_admin_access(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from app.core.security import get_password_hash
    user.hashed_password = get_password_hash(reset_data.new_password)
    db.commit()
    
    logger.info(f"Admin {current_user.email} reset password for user {user.email}")
    return {"message": f"Password for user {user.email} has been reset successfully"}

# ===================== Recruiter Verification Endpoints =====================

@router.get("/recruiters")
async def get_recruiters(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query(None, pattern="^(pending|verified|all)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recruiters (admin only) - filter by status"""
    verify_admin_access(current_user)
    
    query = db.query(RecruiterProfile)
    
    if status == "pending":
        query = query.filter(RecruiterProfile.company_verified == False)
    elif status == "verified":
        query = query.filter(RecruiterProfile.company_verified == True)
    # if status is 'all' or None, return all
    
    recruiters = query.offset(skip).limit(limit).all()
    
    return recruiters

@router.post("/recruiters/{recruiter_id}/verify")
async def verify_recruiter(
    recruiter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a recruiter's company (admin only)"""
    verify_admin_access(current_user)
    
    recruiter = db.query(RecruiterProfile).filter(
        RecruiterProfile.id == recruiter_id
    ).first()
    
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter not found"
        )
    
    if recruiter.company_verified:
        return {"message": "Company already verified"}
    
    recruiter.company_verified = True
    recruiter.verification_token = None
    db.commit()
    
    user = recruiter.user
    logger.info(f"Admin {current_user.email} verified company for recruiter {user.email}")
    return {"message": "Recruiter verified successfully"}

@router.post("/recruiters/{recruiter_id}/reject")
async def reject_recruiter(
    recruiter_id: str,
    reason: str = Query(..., min_length=1, max_length=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a recruiter's company verification (admin only)"""
    verify_admin_access(current_user)
    
    recruiter = db.query(RecruiterProfile).filter(
        RecruiterProfile.id == recruiter_id
    ).first()
    
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter not found"
        )
    
    recruiter.verification_token = None
    db.commit()
    
    user = recruiter.user
    logger.info(f"Admin {current_user.email} rejected recruiter {user.email}. Reason: {reason}")
    return {"message": f"Recruiter rejected. Reason: {reason}"}

# ===================== Statistics Endpoints =====================

@router.get("/stats/overview")
async def get_overview_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get platform overview statistics (admin only)"""
    verify_admin_access(current_user)
    
    try:
        total_users = db.query(User).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        job_seekers = db.query(User).filter(User.role == UserRole.JOB_SEEKER.value).count()
        recruiters = db.query(User).filter(User.role == UserRole.RECRUITER.value).count()
        
        verified_recruiters = db.query(RecruiterProfile).filter(
            RecruiterProfile.company_verified == True
        ).count()
        pending_recruiters = db.query(RecruiterProfile).filter(
            RecruiterProfile.company_verified == False
        ).count()
        
        # Count candidates and matches
        try:
            from app.models.candidate import Candidate
            from app.models.match import Match
            total_candidates = db.query(Candidate).count()
            total_matches = db.query(Match).count()
            total_resumes = db.query(Candidate).filter(Candidate.resume_file_path != None).count()
            applied_matches = db.query(Match).filter(Match.status == 'applied').count()
        except Exception as e:
            logger.error(f"Error counting candidates/matches: {str(e)}")
            total_candidates = 0
            total_matches = 0
            total_resumes = 0
            applied_matches = 0
            
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "active_users": active_users,
            "job_seekers": job_seekers,
            "recruiters": recruiters,
            "verified_recruiters": verified_recruiters,
            "pending_recruiters": pending_recruiters,
            "unverified_users": total_users - verified_users,
            "total_candidates": total_candidates,
            "total_matches": total_matches,
            "applied_matches": applied_matches,
            "total_resumes": total_resumes
        }
    except Exception as e:
        logger.error(f"Error generating overview stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating platform statistics: {str(e)}"
        )

@router.get("/stats/users-by-role")
async def get_users_by_role(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user distribution by role (admin only)"""
    verify_admin_access(current_user)
    
    job_seekers = db.query(User).filter(User.role == UserRole.JOB_SEEKER.value).count()
    recruiters = db.query(User).filter(User.role == UserRole.RECRUITER.value).count()
    admins = db.query(User).filter(User.role == UserRole.ADMIN.value).count()
    
    return {
        "job_seekers": job_seekers,
        "recruiters": recruiters,
        "admins": admins,
        "total": job_seekers + recruiters + admins
    }

@router.get("/stats/verification-status")
async def get_verification_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get verification statistics (admin only)"""
    verify_admin_access(current_user)
    
    verified_users = db.query(User).filter(User.is_verified == True).count()
    unverified_users = db.query(User).filter(User.is_verified == False).count()
    
    verified_recruiters = db.query(RecruiterProfile).filter(
        RecruiterProfile.company_verified == True
    ).count()
    unverified_recruiters = db.query(RecruiterProfile).filter(
        RecruiterProfile.company_verified == False
    ).count()
    
    return {
        "verified_users": verified_users,
        "unverified_users": unverified_users,
        "verified_recruiters": verified_recruiters,
        "unverified_recruiters": unverified_recruiters
    }

# ===================== Activity Log Endpoints =====================

@router.get("/activity-log")
async def get_activity_log(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent user activity (admin only)"""
    verify_admin_access(current_user)
    
    # Get recently active users
    users = db.query(User).order_by(User.last_login.desc()).offset(skip).limit(limit).all()
    
    activity = []
    for user in users:
        activity.append({
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "last_login": user.last_login,
            "is_verified": user.is_verified,
            "is_active": user.is_active
        })
    
    return activity

# ===================== Bulk Embedding Generation =====================

@router.post("/regenerate-embeddings")
async def regenerate_all_embeddings(
    min_match_score: float = Query(0.01, ge=0.0, le=1.0, description="Minimum score for match generation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate embeddings for all jobs and candidates that are missing them,
    then auto-generate matches (admin only)
    """
    verify_admin_access(current_user)
    
    logger.info(f"Admin {current_user.email} initiated bulk embedding regeneration")
    
    # Import services
    from app.services.nlp_processor import NLPProcessor
    from app.services.llm_service import LLMService
    from app.services.matching_engine import MatchingEngine
    from app.core.config import settings
    
    nlp_processor = NLPProcessor(
        spacy_model=settings.SPACY_MODEL,
        embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
    )
    llm_service = LLMService()
    matching_engine = MatchingEngine()
    
    results = {
        "jobs_processed": 0,
        "jobs_failed": 0,
        "candidates_processed": 0,
        "candidates_failed": 0,
        "matches_created": 0,
        "errors": []
    }
    
    # ===== Process Jobs =====
    logger.info("Processing jobs without embeddings...")
    jobs_without_embeddings = db.query(Job).filter(Job.job_embedding == None).all()
    
    for job in jobs_without_embeddings:
        try:
            logger.info(f"Generating embedding for job: {job.title} at {job.company}")
            
            # Generate embedding
            embedding = nlp_processor.generate_embedding(job.description)
            job.job_embedding = embedding
            
            # Normalize title
            try:
                normalized_title = llm_service.normalize_job_title(job.title)
                job.normalized_title = normalized_title
            except Exception as e:
                logger.warning(f"Failed to normalize job title: {e}")
                job.normalized_title = job.title
            
            db.commit()
            results["jobs_processed"] += 1
            logger.info(f"✓ Successfully processed job: {job.title}")
            
        except Exception as e:
            results["jobs_failed"] += 1
            error_msg = f"Failed to process job {job.id} ({job.title}): {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            db.rollback()
    
    # ===== Process Candidates =====
    logger.info("Processing candidates without embeddings...")
    candidates_without_embeddings = db.query(Candidate).filter(
        Candidate.resume_embedding == None,
        Candidate.resume_text != None
    ).all()
    
    for candidate in candidates_without_embeddings:
        try:
            logger.info(f"Generating embedding for candidate: {candidate.name}")
            
            if not candidate.resume_text or len(candidate.resume_text.strip()) == 0:
                error_msg = f"Candidate {candidate.id} ({candidate.name}) has no resume text"
                logger.warning(error_msg)
                results["errors"].append(error_msg)
                results["candidates_failed"] += 1
                continue
            
            # Generate embedding
            embedding = nlp_processor.generate_embedding(candidate.resume_text)
            candidate.resume_embedding = embedding
            
            # Extract skills if missing
            if not candidate.skills:
                categorized_skills = nlp_processor.extract_skills_categorized(candidate.resume_text)
                candidate.skills = categorized_skills
            
            # Generate summary if missing
            if not candidate.resume_summary:
                try:
                    summary = llm_service.summarize_resume(candidate.resume_text)
                    candidate.resume_summary = summary
                except Exception as e:
                    logger.warning(f"Failed to generate summary: {e}")
            
            db.commit()
            results["candidates_processed"] += 1
            logger.info(f"✓ Successfully processed candidate: {candidate.name}")
            
        except Exception as e:
            results["candidates_failed"] += 1
            error_msg = f"Failed to process candidate {candidate.id} ({candidate.name}): {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            db.rollback()
    
    # ===== Generate Matches =====
    logger.info("Generating matches for all candidates...")
    
    # Get all active jobs with embeddings
    active_jobs = db.query(Job).filter(
        Job.is_active == True,
        Job.job_embedding != None
    ).all()
    
    # Get all candidates with embeddings
    candidates_with_embeddings = db.query(Candidate).filter(
        Candidate.resume_embedding != None
    ).all()
    
    logger.info(f"Found {len(active_jobs)} active jobs and {len(candidates_with_embeddings)} candidates with embeddings")
    
    for candidate in candidates_with_embeddings:
        candidate_data = {
            "embedding": candidate.resume_embedding,
            "skills": candidate.skills or [],
            "experience_years": candidate.experience_years or 0
        }
        
        for job in active_jobs:
            try:
                # Check if match already exists
                existing_match = db.query(Match).filter(
                    Match.candidate_id == candidate.id,
                    Match.job_id == job.id
                ).first()
                
                if existing_match:
                    continue
                
                # Calculate match scores
                job_data = {
                    "embedding": job.job_embedding,
                    "required_skills": job.required_skills or [],
                    "experience_required": job.experience_required or 0,
                    "title": job.title
                }
                
                match_scores = matching_engine.match_candidate_to_job(candidate_data, job_data)
                
                # Create match if score meets threshold
                if match_scores["overall_score"] >= min_match_score:
                    try:
                        explanation = llm_service.generate_match_explanation(
                            candidate_data, job_data, match_scores
                        )
                    except Exception as e:
                        logger.warning(f"Failed to generate explanation: {e}")
                        explanation = f"Match score: {match_scores['overall_score']:.2%}"
                    
                    db_match = Match(
                        candidate_id=candidate.id,
                        job_id=job.id,
                        semantic_similarity=match_scores["semantic_similarity"],
                        skill_overlap_score=match_scores["skill_overlap_score"],
                        experience_alignment=match_scores["experience_alignment"],
                        overall_score=match_scores["overall_score"],
                        match_explanation=explanation
                    )
                    
                    db.add(db_match)
                    results["matches_created"] += 1
                    
            except Exception as e:
                error_msg = f"Failed to create match for candidate {candidate.id} and job {job.id}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
    
    try:
        db.commit()
        logger.info(f"✓ Successfully created {results['matches_created']} matches")
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to commit matches: {str(e)}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
    
    # Summary
    logger.info(f"Bulk embedding regeneration complete: {results}")
    
    return {
        "message": "Bulk embedding regeneration completed",
        "summary": {
            "jobs": {
                "processed": results["jobs_processed"],
                "failed": results["jobs_failed"]
            },
            "candidates": {
                "processed": results["candidates_processed"],
                "failed": results["candidates_failed"]
            },
            "matches": {
                "created": results["matches_created"]
            }
        },
        "errors": results["errors"][:10] if results["errors"] else [],  # Limit to first 10 errors
        "total_errors": len(results["errors"])
    }

