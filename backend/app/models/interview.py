"""
Interview Model - scheduling and tracking interviews
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Interview(Base):
    """Interview scheduling and tracking"""
    __tablename__ = "interviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    
    # Relationships
    application = relationship("Application", back_populates="interviews")
    
    recruiter_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False, index=True)

    # Schedule
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)

    # Type & location
    interview_type = Column(String(50), nullable=True)  # phone_screen, technical, behavioral, onsite
    location_or_link = Column(String(512), nullable=True)

    # Status
    status = Column(String(50), default='scheduled', index=True)  # scheduled, completed, cancelled, no_show

    # Notes & feedback
    interviewer_notes = Column(Text, nullable=True)
    candidate_feedback = Column(Text, nullable=True)

    # LLM-generated interview questions
    questions_json = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
