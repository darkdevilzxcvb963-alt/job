"""
Message Model - recruiter-candidate messaging
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
import uuid
from datetime import datetime
from app.core.database import Base


class Message(Base):
    """In-platform messages between recruiters and candidates"""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=True)  # optional context

    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_messages_conversation', 'sender_id', 'receiver_id', 'created_at'),
    )
