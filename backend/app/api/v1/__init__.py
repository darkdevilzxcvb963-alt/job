"""
API v1 Router
"""
from fastapi import APIRouter
from app.api.v1 import (
    candidates, jobs, matches, upload, auth, auth_simple, profiles,
    admin, ai, notifications, feedback, social, privacy,
    bookmarks, skill_gap, interviews, messages, shortlists
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(auth_simple.router, tags=["authentication-simple"])
api_router.include_router(profiles.router, tags=["profiles"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback & analytics"])
api_router.include_router(social.router, prefix="/social", tags=["social integration"])
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy & compliance"])

# New feature routers
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(skill_gap.router, prefix="/skill-gap", tags=["skill gap analysis"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(shortlists.router, prefix="/shortlists", tags=["shortlists"])
