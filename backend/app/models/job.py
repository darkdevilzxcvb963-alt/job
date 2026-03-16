from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class Job(Base):
    """Job posting model"""
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    recruiter_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Job requirements
    required_skills = Column(JSON, nullable=True)  # List of required skills (flat list)
    skills_by_category = Column(JSON, nullable=True)  # Categorized skills (dictionary)
    preferred_skills = Column(JSON, nullable=True)  # List of preferred skills
    experience_required = Column(Float, nullable=True)  # Years of experience
    education_required = Column(JSON, nullable=True)  # Education requirements
    
    # Job details
    location = Column(String(255), nullable=True)
    job_type = Column(String(50), nullable=True)  # full-time, part-time, contract
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    
    # NLP embeddings
    job_embedding = Column(JSON, nullable=True)  # Vector embedding
    normalized_title = Column(String(255), nullable=True)  # LLM-normalized title
    
    # Status
    is_active = Column(Boolean, default=True)
    remote_ok = Column(Boolean, default=False)
    application_deadline = Column(DateTime, nullable=True)
    views_count = Column(Integer, default=0)
    
    # Metadata
    posted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recruiter = relationship("User", backref="jobs")
    matches = relationship("Match", back_populates="job", cascade="all, delete-orphan")
