"""
Candidate Database Model
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Candidate(Base):
    """Candidate/Resume model"""
    __tablename__ = "candidates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    
    # Resume data
    resume_text = Column(Text, nullable=True)
    resume_file_path = Column(String(500), nullable=True)
    resume_file_type = Column(String(10), nullable=True)  # pdf, docx, doc
    
    # Extracted information
    skills = Column(JSON, nullable=True)  # List of skills
    experience_years = Column(Float, nullable=True)
    education = Column(JSON, nullable=True)  # List of education entries
    certifications = Column(JSON, nullable=True)  # List of certifications
    projects = Column(JSON, nullable=True)  # List of projects
    
    # NLP embeddings
    resume_embedding = Column(JSON, nullable=True)  # Vector embedding
    resume_summary = Column(Text, nullable=True)  # LLM-generated summary
    seniority_level = Column(String(50), nullable=True)  # Entry-level, Junior, Mid, Senior, Lead, Director
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matches = relationship("Match", back_populates="candidate", cascade="all, delete-orphan")
