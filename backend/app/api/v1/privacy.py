"""
Security & Compliance Middleware
Implements security headers, GDPR data export, and privacy controls.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime
import json

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.candidate import Candidate
from app.models.match import Match


# ─── Security Headers Middleware ─────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses (OWASP best practices)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response


# ─── GDPR / Privacy API ─────────────────────────────────────────────────────

router = APIRouter()


@router.get("/my-data")
async def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GDPR Article 20: Right to Data Portability.
    Export all personal data associated with the current user.
    """
    user_data = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "created_at": str(current_user.created_at) if current_user.created_at else None,
            "is_verified": current_user.is_verified,
        },
        "exported_at": datetime.utcnow().isoformat(),
        "data_categories": []
    }

    # Include candidate data if applicable
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if candidate:
        user_data["candidate_profile"] = {
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "skills": candidate.skills,
            "experience_years": candidate.experience_years,
            "resume_summary": candidate.resume_summary,
        }
        user_data["data_categories"].append("candidate_profile")

        # Include matches
        matches = db.query(Match).filter(Match.candidate_id == candidate.id).all()
        user_data["matches"] = [
            {
                "job_id": m.job_id,
                "overall_score": m.overall_score,
                "status": m.status,
                "created_at": str(m.created_at),
                "feedback_rating": m.feedback_rating,
            }
            for m in matches
        ]
        user_data["data_categories"].append("matches")

    return user_data


@router.delete("/my-data")
async def request_data_deletion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GDPR Article 17: Right to Erasure ('Right to be Forgotten').
    Request deletion of all personal data.
    Note: This creates a deletion request; actual deletion may be deferred for audit.
    """
    # GDPR Article 17 implementation: Mark user as inactive and record deletion timestamp
    current_user.is_active = False
    current_user.deletion_requested_at = datetime.utcnow()
    
    db.add(current_user)
    db.commit()
    
    logger.warning(f"Data deletion requested by user {current_user.email} (id={current_user.id}). Account deactivated.")

    return {
        "status": "deletion_requested",
        "user_id": current_user.id,
        "message": "Your account has been deactivated and a data deletion request has been recorded. "
                   "Your data will be permanently deleted within 30 days as required by GDPR. "
                   "You will receive a final confirmation email when the process is complete.",
        "requested_at": current_user.deletion_requested_at.isoformat()
    }


@router.get("/privacy-policy")
async def get_privacy_policy():
    """Return the platform's privacy policy summary."""
    return {
        "title": "Privacy Policy - AI Resume Matching Platform",
        "last_updated": "2026-03-09",
        "sections": {
            "data_collected": [
                "Name, email, phone number (account creation)",
                "Resume text and extracted skills (job matching)",
                "Job interaction data (applications, feedback)",
            ],
            "data_usage": [
                "AI-powered job matching and recommendations",
                "Platform analytics (aggregated, anonymized)",
                "Communication (notifications about matches)",
            ],
            "data_retention": "Personal data retained for active accounts. Deleted within 30 days of deletion request.",
            "third_party_sharing": "No personal data is sold. Limited sharing with consented social platform integrations only.",
            "user_rights": [
                "Right to access (GET /api/v1/privacy/my-data)",
                "Right to erasure (DELETE /api/v1/privacy/my-data)",
                "Right to rectification (PUT /api/v1/auth/me)",
                "Right to data portability (GET /api/v1/privacy/my-data)",
            ],
            "compliance": ["GDPR (EU)", "CCPA (California)", "EEOC (Anti-discrimination)"]
        }
    }
