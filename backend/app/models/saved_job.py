"""
Saved Job Model - allows candidates to bookmark jobs
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class SavedJob(Base):
    """Candidate's bookmarked/saved jobs"""
    __tablename__ = "saved_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="saved_jobs")

    __table_args__ = (UniqueConstraint('user_id', 'job_id', name='uq_user_job'),)
