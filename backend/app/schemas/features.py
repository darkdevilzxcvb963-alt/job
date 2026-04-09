"""
Pydantic schemas for new platform features
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ========== Saved Jobs / Bookmarks ==========

class SavedJobCreate(BaseModel):
    job_id: str
    notes: Optional[str] = None

class SavedJobResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    notes: Optional[str] = None
    created_at: datetime
    # Joined job details
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        from_attributes = True


# ========== Interviews ==========

class InterviewCreate(BaseModel):
    application_id: str
    candidate_id: str
    scheduled_at: datetime
    duration_minutes: int = 60
    interview_type: Optional[str] = None  # phone_screen, technical, behavioral, onsite
    location_or_link: Optional[str] = None

class InterviewUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    interview_type: Optional[str] = None
    location_or_link: Optional[str] = None
    status: Optional[str] = None
    interviewer_notes: Optional[str] = None
    candidate_feedback: Optional[str] = None

class InterviewResponse(BaseModel):
    id: str
    application_id: str
    recruiter_id: str
    candidate_id: str
    scheduled_at: datetime
    duration_minutes: int
    interview_type: Optional[str] = None
    location_or_link: Optional[str] = None
    status: str
    interviewer_notes: Optional[str] = None
    candidate_feedback: Optional[str] = None
    questions_json: Optional[list] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Messages ==========

class MessageCreate(BaseModel):
    receiver_id: str
    content: str
    match_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    match_id: Optional[str] = None
    content: str
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        }

class ConversationSummary(BaseModel):
    other_user_id: str
    other_user_name: str
    last_message: str
    last_message_at: datetime
    unread_count: int


# ========== Shortlists ==========

class ShortlistCreate(BaseModel):
    name: str
    job_id: Optional[str] = None

class ShortlistAddCandidate(BaseModel):
    candidate_id: str
    notes: Optional[str] = None

class ShortlistResponse(BaseModel):
    id: str
    recruiter_id: str
    name: str
    job_id: Optional[str] = None
    candidate_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Skill Gap Analysis ==========

class SkillGapRequest(BaseModel):
    candidate_id: str
    job_id: str

class SkillGapMissing(BaseModel):
    skill: str
    severity: str  # critical, moderate, low
    category: str = "General"

class SkillGapBridgeable(BaseModel):
    skill: str
    severity: str = "moderate"
    category: str = "General"
    you_know: str = ""
    learning_path: str = ""

class SkillGapRecommendation(BaseModel):
    skill: str
    course: str
    platform: str = "Online Learning"
    duration: str = "4-6 weeks"
    url: str = ""

class SkillGapResponse(BaseModel):
    coverage_score: float
    matched_skills: List[str]
    missing_skills: List[SkillGapMissing]
    bridgeable_skills: List[SkillGapBridgeable]
    recommendations: List[SkillGapRecommendation] = []
    total_required: int = 0
    total_matched: int = 0


# ========== Resume Scoring ==========

class ResumeSectionScore(BaseModel):
    found: bool
    score: float
    label: str

class ResumeScoreResponse(BaseModel):
    overall_score: float
    grade: str
    section_scores: Dict[str, ResumeSectionScore]
    keyword_score: float
    formatting_score: float
    length_score: float
    impact_score: float = 0.0
    feedback: List[str]
