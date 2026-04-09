"""
User Profile Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import json
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole, CandidateProfile, RecruiterProfile
from app.schemas.auth import (
    CandidateProfileUpdate,
    CandidateProfileResponse,
    RecruiterProfileUpdate,
    RecruiterProfileResponse
)
from loguru import logger

router = APIRouter(prefix="/profiles", tags=["profiles"])

# ===================== Candidate Profile Endpoints =====================

@router.get("/candidate/me", response_model=CandidateProfileResponse)
async def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current candidate profile"""
    if current_user.role not in [UserRole.JOB_SEEKER.value, UserRole.ADMIN.value]:
        logger.warning(f"Permission denied for get_candidate_profile: user {current_user.email} has role {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can access candidate profiles"
        )
    
    candidate = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    
    return candidate

@router.post("/candidate/me", response_model=CandidateProfileResponse)
async def create_or_update_candidate_profile(
    profile_data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update candidate profile"""
    if current_user.role not in [UserRole.JOB_SEEKER.value, UserRole.ADMIN.value]:
        logger.warning(f"Permission denied for create_or_update_candidate_profile: user {current_user.email} has role {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can create candidate profiles"
        )
    
    candidate = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    
    if not candidate:
        # Create new candidate profile
        candidate = CandidateProfile(user_id=current_user.id)
        db.add(candidate)
    
    # Update fields if provided
    if profile_data.headline is not None:
        candidate.headline = profile_data.headline
    if profile_data.years_of_experience is not None:
        candidate.years_of_experience = profile_data.years_of_experience
    if profile_data.skills is not None:
        candidate.skills = profile_data.skills
    if profile_data.expertise_areas is not None:
        candidate.expertise_areas = profile_data.expertise_areas
    if profile_data.preferred_locations is not None:
        candidate.preferred_locations = profile_data.preferred_locations
    if profile_data.preferred_job_types is not None:
        candidate.preferred_job_types = profile_data.preferred_job_types
    if profile_data.salary_expectation_min is not None:
        candidate.salary_expectation_min = profile_data.salary_expectation_min
    if profile_data.salary_expectation_max is not None:
        candidate.salary_expectation_max = profile_data.salary_expectation_max
    
    # Update user profile data
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.location is not None:
        current_user.location = profile_data.location
    
    # Calculate profile completion percentage
    completed_fields = 0
    total_fields = 9
    
    if candidate.headline:
        completed_fields += 1
    if candidate.years_of_experience:
        completed_fields += 1
    if candidate.skills:
        completed_fields += 1
    if candidate.expertise_areas:
        completed_fields += 1
    if candidate.preferred_locations:
        completed_fields += 1
    if candidate.preferred_job_types:
        completed_fields += 1
    if candidate.salary_expectation_min:
        completed_fields += 1
    if candidate.salary_expectation_max:
        completed_fields += 1
    if current_user.bio:
        completed_fields += 1
    
    candidate.profile_completion_percentage = (completed_fields / total_fields) * 100
    candidate.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(candidate)
    
    logger.info(f"Candidate profile updated for user: {current_user.email}")
    return candidate

@router.get("/recruiter/me", response_model=RecruiterProfileResponse)
async def get_recruiter_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current recruiter profile"""
    if current_user.role != UserRole.RECRUITER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access recruiter profiles"
        )
    
    recruiter = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
    
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )
    
    return recruiter

@router.post("/recruiter/me", response_model=RecruiterProfileResponse)
async def create_or_update_recruiter_profile(
    profile_data: RecruiterProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update recruiter profile"""
    # Allow both recruiters and admins to manage recruiter profiles
    logger.info(f"Updating recruiter profile for user: {current_user.email}, role: {current_user.role}")
    if current_user.role not in [UserRole.RECRUITER.value, UserRole.ADMIN.value]:
        logger.warning(f"Permission denied for recruiter profile update: user {current_user.email} has role {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only recruiters can create recruiter profiles (your role: {current_user.role})"
        )
    
    recruiter = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
    logger.info(f"Existing recruiter profile found: {recruiter is not None}")
    
    if not recruiter:
        logger.info("Creating new recruiter profile")
        if not profile_data.company_name:
            logger.warning("Missing company name for new recruiter profile")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name is required for new recruiter profiles"
            )
        
        recruiter = RecruiterProfile(
            user_id=current_user.id,
            company_name=profile_data.company_name or "Unknown Company"
        )
        db.add(recruiter)
    
    try:
        # Update fields if provided
        if profile_data.company_name is not None:
            recruiter.company_name = profile_data.company_name
        if profile_data.company_website is not None:
            recruiter.company_website = profile_data.company_website
        if profile_data.company_description is not None:
            recruiter.company_description = profile_data.company_description
        if profile_data.company_size is not None:
            recruiter.company_size = profile_data.company_size
        if profile_data.company_industry is not None:
            recruiter.company_industry = profile_data.company_industry
        if profile_data.job_title is not None:
            recruiter.job_title = profile_data.job_title
        if profile_data.department is not None:
            recruiter.department = profile_data.department
        
        # Update user profile data
        if profile_data.bio is not None:
            current_user.bio = profile_data.bio
        if profile_data.location is not None:
            current_user.location = profile_data.location
        
        # Update hiring preferences
        logger.info("Updating JSON hiring preferences")
        if profile_data.roles_hiring_for is not None:
            recruiter.roles_hiring_for = profile_data.roles_hiring_for
        if profile_data.experience_range is not None:
            recruiter.experience_range = profile_data.experience_range
        if profile_data.job_types is not None:
            recruiter.job_types = profile_data.job_types
        if profile_data.work_modes is not None:
            recruiter.work_modes = profile_data.work_modes
            
        # Update job defaults
        if profile_data.default_skills is not None:
            recruiter.default_skills = profile_data.default_skills
        if profile_data.default_location is not None:
            recruiter.default_location = profile_data.default_location
        if profile_data.default_deadline is not None:
            recruiter.default_deadline = profile_data.default_deadline
        
        recruiter.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(recruiter)
        
        logger.info(f"Recruiter profile updated for user: {current_user.email}")
        return recruiter
    except Exception as e:
        import traceback
        error_tb = traceback.format_exc()
        logger.error(f"Failed to update recruiter profile: {str(e)}\n{error_tb}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error saving profile: {str(e)}"
        )
