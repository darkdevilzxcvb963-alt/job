"""
Job Pydantic Schemas
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobBase(BaseModel):
    """Base job schema"""
    title: str
    company: str
    description: str
    location: Optional[str] = None
    job_type: Optional[str] = None

class JobCreate(JobBase):
    """Schema for creating a job"""
    required_skills: Optional[List[str]] = None
    skills_by_category: Optional[dict] = None
    preferred_skills: Optional[List[str]] = None
    experience_required: Optional[float] = None
    education_required: Optional[List[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None

class JobUpdate(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    required_skills: Optional[List[str]] = None
    skills_by_category: Optional[dict] = None

class JobResponse(JobBase):
    """Schema for job response"""
    id: str
    required_skills: Optional[List[str]] = None
    skills_by_category: Optional[dict] = None
    preferred_skills: Optional[List[str]] = None
    experience_required: Optional[float] = None
    normalized_title: Optional[str] = None
    is_active: bool
    recruiter_id: Optional[str] = None
    posted_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
