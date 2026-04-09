"""
Notification Dispatcher for Production
Orchestrates multi-channel notifications based on user preferences.
"""
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.notification import Notification
from app.models.profile_settings import NotificationPreferences
from app.services.notification_service import NotificationService
from app.models.user import User

class NotificationDispatcher:
    """Production dispatcher to handle Email, SMS, Push, and In-app channels"""
    
    def __init__(self, db: Session):
        self.db = db
        self.service = NotificationService()

    async def dispatch(self, user_id: str, title: str, message: str, type: str, related_id: str = None):
        """Dispatch a notification to all enabled channels for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found for notification dispatch")
            return

        # 1. Get user preferences
        prefs = self.db.query(NotificationPreferences).filter(
            NotificationPreferences.user_id == user_id
        ).first()
        
        # Default to enabling basic channels if no prefs found
        email_enabled = prefs.email_jobs if prefs else True
        sms_enabled = prefs.sms_alerts if prefs else False
        push_enabled = prefs.push_notifications if prefs else True
        
        # 2. Always create In-app notification record
        in_app = Notification(
            user_id=user_id,
            type=type,
            message=message,
            related_match_id=related_id if type == 'job_match' else None
        )
        self.db.add(in_app)
        self.db.commit()

        # 3. Dispatch to Email
        if email_enabled:
            await self.service.send_email(user.email, title, f"<h3>{title}</h3><p>{message}</p>")
            
        # 4. Dispatch to SMS
        if sms_enabled and user.phone:
            await self.service.send_sms(user.phone, f"{title}: {message}")
            
        # 5. Dispatch to Push
        if push_enabled:
            await self.service.send_push_notification(user_id, title, message)

        logger.info(f"Notification '{type}' dispatched to {user.email} (Channels: Email={email_enabled}, SMS={sms_enabled}, Push={push_enabled})")

    @staticmethod
    async def notify_new_match(db: Session, user_id: str, job_title: str, match_score: float, job_id: str):
        """Specifically handle a new high-quality match notification"""
        dispatcher = NotificationDispatcher(db)
        title = "🎯 New High-Score Match!"
        message = f"We found a new job match for you: '{job_title}' with a {int(match_score*100)}% fit score."
        await dispatcher.dispatch(user_id, title, message, "job_match", job_id)
