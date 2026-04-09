"""
User Database Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Text, Float, ForeignKey, JSON
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    """User role enumeration"""
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class User(Base):
    """Base User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    # role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.JOB_SEEKER, index=True)
    role = Column(String(50), nullable=False, default="job_seeker", index=True)
    
    # Authentication Provider Tracking
    auth_provider = Column(String(50), nullable=True, default="local", index=True)
    auth_provider_id = Column(String(255), nullable=True, index=True)
    
    # Profile Information
    profile_picture_url = Column(String(512), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    
    # Verification status
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Email verification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # MFA / Security
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)
    mfa_type = Column(String(50), nullable=True) # e.g. 'otp', 'email', 'backup_codes'
    mfa_backup_codes = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    deletion_requested_at = Column(DateTime, nullable=True)
    
    # Relationships
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recruiter_profile = relationship("RecruiterProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class CandidateProfile(Base):
    """Candidate profile model for job seekers (extended user profile)"""
    __tablename__ = "candidate_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Professional Info
    headline = Column(String(255), nullable=True)
    resume_url = Column(String(512), nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    skills = Column(JSON, nullable=True)  # JSON list of skills
    expertise_areas = Column(JSON, nullable=True)  # JSON list
    
    # Preferences
    preferred_locations = Column(JSON, nullable=True)  # JSON list
    preferred_job_types = Column(JSON, nullable=True)  # JSON list (full-time, part-time, contract, etc)
    salary_expectation_min = Column(Float, nullable=True)
    salary_expectation_max = Column(Float, nullable=True)
    
    # Social
    linkedin_url = Column(String(512), nullable=True)
    
    # Extended Preferences (for matching engine)
    preferred_roles = Column(JSON, nullable=True)          # JSON list of roles
    work_mode = Column(String(20), nullable=True)          # remote / hybrid / on-site
    industry = Column(String(255), nullable=True)
    notice_period = Column(String(50), nullable=True)      # e.g. "immediate", "2 weeks", "1 month"
    open_to_work = Column(Boolean, default=True, nullable=False)
    
    # Visibility
    is_discoverable = Column(Boolean, default=True, nullable=False)
    
    # Profile completion
    profile_completion_percentage = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile", foreign_keys=[user_id])

class RecruiterProfile(Base):
    """Recruiter profile model for employers (extended user profile)"""
    __tablename__ = "recruiter_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Company Info
    company_name = Column(String(255), nullable=False, index=True)
    company_website = Column(String(512), nullable=True)
    company_logo_url = Column(String(512), nullable=True)
    company_description = Column(Text, nullable=True)
    company_size = Column(String(50), nullable=True)  # small, medium, large, enterprise
    company_industry = Column(String(255), nullable=True)
    
    # Recruiter Info
    job_title = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    
    # Verification
    company_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    
    # Stats
    total_jobs_posted = Column(Integer, default=0)
    active_job_postings = Column(Integer, default=0)
    
    # Hiring Preferences (Simple)
    roles_hiring_for = Column(JSON, nullable=True)     # JSON list of roles
    experience_range = Column(String(100), nullable=True) # e.g. "0-2 yrs", "2-5 yrs"
    job_types = Column(JSON, nullable=True)            # JSON list (Full-time, Internship)
    work_modes = Column(JSON, nullable=True)           # JSON list (Remote, On-site)
    
    # Job Posting Defaults
    default_skills = Column(JSON, nullable=True)       # JSON list of skills
    default_location = Column(String(255), nullable=True)
    default_deadline = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="recruiter_profile", foreign_keys=[user_id])
