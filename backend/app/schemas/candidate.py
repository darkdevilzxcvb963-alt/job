"""
Candidate Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime

class CandidateBase(BaseModel):
    """Base candidate schema"""
    name: str
    email: EmailStr
    phone: Optional[str] = None

class CandidateCreate(CandidateBase):
    """Schema for creating a candidate"""
    pass

class CandidateUpdate(BaseModel):
    """Schema for updating a candidate"""
    name: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[Any] = None
    experience_years: Optional[float] = None

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
