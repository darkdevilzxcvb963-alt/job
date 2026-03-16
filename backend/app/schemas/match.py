"""
Match Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.intelligence import MatchIntelligence

class MatchResponse(BaseModel):
    """Schema for match response"""
    id: str
    candidate_id: str
    job_id: str
    semantic_similarity: float
    skill_overlap_score: float
    experience_alignment: float
    overall_score: float
    match_explanation: Optional[str] = None
    status: str = "matched"
    created_at: datetime
    
    class Config:
        from_attributes = True

class MatchWithDetails(MatchResponse):
    """Match response with candidate and job details"""
    candidate_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None
    candidate_resume_path: Optional[str] = None
    candidate_resume_summary: Optional[str] = None
    candidate_skills: Optional[list] = None
    candidate_user_id: Optional[str] = None
    
    # Enhanced Job details for UI
    job_title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    required_skills: Optional[list] = None
    preferred_skills: Optional[list] = None
    experience_required: Optional[float] = None
    education_required: Optional[list] = None
    status: str = "matched"
    cover_letter: Optional[str] = None
    intelligence: Optional[MatchIntelligence] = None
    # Recruiter contact info (visible to the candidate)
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    recruiter_phone: Optional[str] = None
    
    class Config:
        from_attributes = True
