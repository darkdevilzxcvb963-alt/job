"""
Candidate Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime

class CandidateBase(BaseModel):
    """Base candidate schema"""
    name: str
    email: str
    phone: Optional[str] = None

class CandidateCreate(CandidateBase):
    """Schema for creating a candidate"""
    pass

class CandidateUpdate(BaseModel):
    """Schema for updating a candidate"""
    name: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    skills: Optional[Any] = None
    experience_years: Optional[float] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    salary_expectation_min: Optional[float] = None
    salary_expectation_max: Optional[float] = None
    notice_period: Optional[str] = None
    work_mode: Optional[str] = None
    industry: Optional[str] = None
    open_to_work: Optional[bool] = None

class CandidateResponse(CandidateBase):
    """Schema for candidate response"""
    id: str
    skills: Optional[Any] = None
    experience_years: Optional[float] = None
    education: Optional[List[dict]] = None
    certifications: Optional[List[str]] = None
    resume_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProcessResumeRequest(BaseModel):
    """Schema for resume processing request"""
    file_path: str
