"""
Profile Settings Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Experience ────────────────────────────────────────────────────────────────

class ExperienceCreate(BaseModel):
    job_title: str = Field(..., max_length=255)
    company: str = Field(..., max_length=255)
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None

class ExperienceUpdate(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None

class ExperienceResponse(BaseModel):
    id: str
    user_id: str
    job_title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── Education ─────────────────────────────────────────────────────────────────

class EducationCreate(BaseModel):
    degree: str = Field(..., max_length=255)
    institution: str = Field(..., max_length=255)
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None

class EducationUpdate(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None

class EducationResponse(BaseModel):
    id: str
    user_id: str
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── Projects ──────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── Certifications ────────────────────────────────────────────────────────────

class CertificationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    provider: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_url: Optional[str] = None
    credential_id: Optional[str] = None

class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_url: Optional[str] = None
    credential_id: Optional[str] = None

class CertificationResponse(BaseModel):
    id: str
    user_id: str
    name: str
    provider: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_url: Optional[str] = None
    credential_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── Job Preferences ───────────────────────────────────────────────────────────

class JobPreferencesUpdate(BaseModel):
    headline: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    salary_expectation_min: Optional[float] = None
    salary_expectation_max: Optional[float] = None
    work_mode: Optional[str] = None             # remote / hybrid / on-site
    industry: Optional[str] = None
    notice_period: Optional[str] = None
    open_to_work: Optional[bool] = None

class JobPreferencesResponse(BaseModel):
    headline: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    salary_expectation_min: Optional[float] = None
    salary_expectation_max: Optional[float] = None
    work_mode: Optional[str] = None
    industry: Optional[str] = None
    notice_period: Optional[str] = None
    open_to_work: bool = True
    class Config:
        from_attributes = True


# ── AI Settings ───────────────────────────────────────────────────────────────

class AISettingsUpdate(BaseModel):
    matching_mode: Optional[str] = None          # strict / balanced / exploratory
    skill_weight: Optional[int] = Field(None, ge=0, le=100)
    experience_weight: Optional[int] = Field(None, ge=0, le=100)
    education_weight: Optional[int] = Field(None, ge=0, le=100)

class AISettingsResponse(BaseModel):
    matching_mode: str = "balanced"
    skill_weight: int = 40
    experience_weight: int = 35
    education_weight: int = 25
    class Config:
        from_attributes = True


# ── Notification Preferences ─────────────────────────────────────────────────

class NotificationPreferencesUpdate(BaseModel):
    email_jobs: Optional[bool] = None
    email_messages: Optional[bool] = None
    sms_alerts: Optional[bool] = None
    push_notifications: Optional[bool] = None
    frequency: Optional[str] = None              # instant / daily / weekly

class NotificationPreferencesResponse(BaseModel):
    email_jobs: bool = True
    email_messages: bool = True
    sms_alerts: bool = False
    push_notifications: bool = True
    frequency: str = "instant"
    class Config:
        from_attributes = True


# ── Privacy Settings ──────────────────────────────────────────────────────────

class PrivacySettingsUpdate(BaseModel):
    profile_visibility: Optional[str] = None     # public / recruiters / private
    resume_visible: Optional[bool] = None
    contact_visible: Optional[bool] = None
    blocked_companies: Optional[List[str]] = None

class PrivacySettingsResponse(BaseModel):
    profile_visibility: str = "public"
    resume_visible: bool = True
    contact_visible: bool = True
    blocked_companies: Optional[List[str]] = None
    class Config:
        from_attributes = True


# ── Profile Strength ─────────────────────────────────────────────────────────

class ProfileStrengthResponse(BaseModel):
    percentage: float
    completed: List[str]
    missing: List[str]
    suggestions: List[str]
