"""
Profile Settings Models — Experience, Education, Projects, Certifications,
AI Settings, Notification/Privacy Preferences, Activity Logs
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class UserExperience(Base):
    """Work experience entries for a user"""
    __tablename__ = "user_experiences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    start_date = Column(String(20), nullable=True)   # YYYY-MM format
    end_date = Column(String(20), nullable=True)      # YYYY-MM or "present"
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)         # Rich text for embeddings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserEducation(Base):
    """Education entries for a user"""
    __tablename__ = "user_education"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    grade = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserProject(Base):
    """Project entries for a user"""
    __tablename__ = "user_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tech_stack = Column(JSON, nullable=True)          # List of technologies
    github_url = Column(String(512), nullable=True)
    demo_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserCertification(Base):
    """Certification entries for a user"""
    __tablename__ = "user_certifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=True)
    issue_date = Column(String(20), nullable=True)    # YYYY-MM
    expiry_date = Column(String(20), nullable=True)
    credential_url = Column(String(512), nullable=True)
    credential_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AISettings(Base):
    """AI personalization settings per user"""
    __tablename__ = "ai_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    matching_mode = Column(String(20), default="balanced")   # strict / balanced / exploratory
    skill_weight = Column(Integer, default=40)               # 0-100
    experience_weight = Column(Integer, default=35)           # 0-100
    education_weight = Column(Integer, default=25)            # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationPreferences(Base):
    """Notification preferences per user"""
    __tablename__ = "notification_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    email_jobs = Column(Boolean, default=True)
    email_messages = Column(Boolean, default=True)
    sms_alerts = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    frequency = Column(String(20), default="instant")   # instant / daily / weekly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PrivacySettings(Base):
    """Privacy settings per user"""
    __tablename__ = "privacy_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    profile_visibility = Column(String(20), default="public")   # public / recruiters / private
    resume_visible = Column(Boolean, default=True)
    contact_visible = Column(Boolean, default=True)
    blocked_companies = Column(JSON, nullable=True)              # List of company names
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserActivityLog(Base):
    """Tracks user behaviour for AI improvement (clicks, applications, skips)"""
    __tablename__ = "user_activity_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)    # click, apply, skip, like, dislike
    entity_type = Column(String(50), nullable=True)            # job, match, recommendation
    entity_id = Column(String(36), nullable=True)
    extra_data = Column(JSON, nullable=True)                  # arbitrary JSON payload
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
