"""
Shortlist Models - recruiter candidate shortlisting
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Shortlist(Base):
    """Named shortlist created by a recruiter for a specific job"""
    __tablename__ = "shortlists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    recruiter_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="shortlists")


class ShortlistCandidate(Base):
    """Candidate added to a shortlist"""
    __tablename__ = "shortlist_candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    shortlist_id = Column(String(36), ForeignKey("shortlists.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('shortlist_id', 'candidate_id', name='uq_shortlist_candidate'),)
