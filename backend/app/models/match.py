"""
Job-Candidate Match Database Model
"""
from sqlalchemy import Column, Integer, Float, DateTime, Text, ForeignKey, String
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Match(Base):
    """Match between candidate and job"""
    __tablename__ = "matches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    
    # Matching scores
    semantic_similarity = Column(Float, nullable=False)  # Cosine similarity
    skill_overlap_score = Column(Float, nullable=False)
    experience_alignment = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False, index=True)  # Combined job-fit score
    
    # Extended scoring factors
    location_score = Column(Float, nullable=True)
    salary_score = Column(Float, nullable=True)
    seniority_score = Column(Float, nullable=True)
    
    # LLM-generated explanation
    match_explanation = Column(Text, nullable=True)
    
    # Status: matched, applied, rejected, etc.
    status = Column(String(50), default='matched', index=True)
    
    # User feedback on match quality
    feedback_rating = Column(Integer, nullable=True)  # -1 (bad), 1 (good), or 1-5 stars
    feedback_reason = Column(String(200), nullable=True)  # "not_relevant", "wrong_skills", etc.
    feedback_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="matches")
    job = relationship("Job", back_populates="matches")
    application = relationship("Application", back_populates="match", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", backref="match", cascade="all, delete-orphan")
    messages = relationship("Message", backref="match", cascade="all, delete-orphan")
