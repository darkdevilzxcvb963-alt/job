"""
Career Intelligence Models — Skill Gaps, Career Suggestions, and Resume Versions
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class SkillGapAnalysis(Base):
    """Stores AI-calculated skill gaps between a user and a target job/market"""
    __tablename__ = "skill_gap_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = Column(String(255), nullable=True)
    gap_data = Column(JSON, nullable=False)           # {missing_skills: [], proficiency_gaps: {}}
    match_score = Column(Float, default=0.0)
    suggestions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class CareerSuggestion(Base):
    """AI-generated career path and improvement suggestions"""
    __tablename__ = "career_suggestions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")   # low, medium, high
    category = Column(String(50), nullable=True)     # skills, resume, experience
    is_completed = Column(Boolean, default=False)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class ResumeVersion(Base):
    """Tracking different versions of a user's resume for tailoring and historical data"""
    __tablename__ = "resume_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1)
    file_path = Column(String(512), nullable=False)
    file_name = Column(String(255), nullable=True)
    parsed_text = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
