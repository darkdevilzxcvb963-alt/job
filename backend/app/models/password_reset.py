"""
Password Reset Database Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class PasswordReset(Base):
    """Password reset token model"""
    __tablename__ = "password_resets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="password_resets")
