"""
Notification Model - in-app notifications for recruiters
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
import uuid
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    """In-app notifications, e.g. recruiter notified when candidate applies"""
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)  # recipient (recruiter)
    type = Column(String(50), nullable=False)  # e.g. 'application_received'
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    related_match_id = Column(String(36), ForeignKey("matches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
