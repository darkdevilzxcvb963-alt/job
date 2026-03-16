"""
AI Service Schemas
"""
from pydantic import BaseModel
from typing import List, Optional, Dict

class OutreachRequest(BaseModel):
    candidate_name: str
    job_title: str
    company: str
    match_explanation: str

class OutreachResponse(BaseModel):
    message: str

class JDGenRequest(BaseModel):
    title: str
    key_points: str

class JDGenResponse(BaseModel):
    job_description: str

class InterviewPrepRequest(BaseModel):
    candidate_skills: List[str]
    job_requirements: List[str]
    job_title: str

class InterviewPrepResponse(BaseModel):
    questions: List[str]

class SmartSearchRequest(BaseModel):
    query: str
    limit: int = 10

class SmartSearchCandidate(BaseModel):
    id: str
    name: str
    email: str
    score: float
    skills: Optional[Dict[str, List[str]]] = None
    experience_years: Optional[float] = None
    summary: Optional[str] = None

class SmartSearchResponse(BaseModel):
    results: List[SmartSearchCandidate]
