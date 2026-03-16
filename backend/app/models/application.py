"""
Job Application Model - tracks candidate applications with cover letters
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Application(Base):
    """Stores detailed application info when a candidate applies to a job"""
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False, unique=True)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)

    cover_letter = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    match = relationship("Match", backref="application")
    candidate = relationship("Candidate", backref="applications")
    job = relationship("Job", backref="applications")
