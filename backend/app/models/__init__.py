"""
Database Models
"""
from app.models.password_reset import PasswordReset
from app.models.user_session import UserSession
from app.models.auth_tokens import RefreshToken, OTPToken, LoginAttempt, VerificationToken
from app.models.profile_settings import (
    UserExperience, UserEducation, UserProject, UserCertification,
    AISettings, NotificationPreferences, PrivacySettings, UserActivityLog
)
from app.models.intelligence import SkillGapAnalysis, CareerSuggestion, ResumeVersion
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.models.user import User, UserRole, CandidateProfile, RecruiterProfile
from app.models.application import Application
from app.models.interview import Interview
from app.models.shortlist import Shortlist
from app.models.saved_job import SavedJob
from app.models.notification import Notification
from app.models.message import Message

__all__ = [
    "Candidate",
    "Job",
    "Match",
    "User",
    "UserRole",
    "CandidateProfile",
    "RecruiterProfile",
    "Application",
    "Interview",
    "Shortlist",
    "SavedJob",
    "Notification",
    "Message",
    "PasswordReset",
    "UserSession",
    "RefreshToken",
    "OTPToken",
    "LoginAttempt",
    "VerificationToken",
    "UserExperience",
    "UserEducation", 
    "UserProject",
    "UserCertification",
    "AISettings",
    "NotificationPreferences",
    "PrivacySettings",
    "UserActivityLog",
    "SkillGapAnalysis",
    "CareerSuggestion",
    "ResumeVersion"
]

