"""
Skill Gap Analysis Model - stores skill gap analysis results
"""
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
import uuid
from datetime import datetime
from app.core.database import Base


class SkillGapAnalysis(Base):
    """Stored skill gap analysis between a candidate and a target job"""
    __tablename__ = "skill_gap_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)

    # Analysis results
    missing_skills = Column(JSON, nullable=True)      # ["AWS", "Docker", ...]
    matched_skills = Column(JSON, nullable=True)       # ["Python", "React", ...]
    bridgeable_skills = Column(JSON, nullable=True)    # [{"skill": "K8s", "you_know": "Docker"}]
    recommendations = Column(JSON, nullable=True)      # [{"skill": "AWS", "course": "...", "duration": "4w"}]
    coverage_score = Column(Float, nullable=True)      # 0.0 to 1.0

    created_at = Column(DateTime, default=datetime.utcnow)
