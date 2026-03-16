"""
Social Integration API Endpoints
Handles GitHub/LinkedIn profile enrichment, social sharing, and referrals.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.social_integration import SocialIntegrationService

router = APIRouter()
_social_service = None

def get_social_service():
    global _social_service
    if _social_service is None:
        _social_service = SocialIntegrationService()
    return _social_service


class GitHubEnrichRequest(BaseModel):
    github_username: str

class LinkedInEnrichRequest(BaseModel):
    linkedin_url: str

class ShareRequest(BaseModel):
    job_title: str
    company: str
    job_url: str

class ReferralRequest(BaseModel):
    job_id: str


@router.post("/enrich/github")
async def enrich_from_github(
    request: GitHubEnrichRequest,
    current_user: User = Depends(get_current_user)
):
    """Enrich candidate profile with public GitHub data (requires user consent)."""
    service = get_social_service()
    result = service.enrich_from_github(request.github_username)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/enrich/linkedin")
async def enrich_from_linkedin(
    request: LinkedInEnrichRequest,
    current_user: User = Depends(get_current_user)
):
    """Placeholder for LinkedIn enrichment (requires OAuth2 approval)."""
    service = get_social_service()
    return service.enrich_from_linkedin(request.linkedin_url)


@router.post("/share-links")
async def generate_share_links(request: ShareRequest):
    """Generate social media sharing links for a job posting."""
    service = get_social_service()
    return service.generate_share_links(request.job_title, request.company, request.job_url)


@router.post("/referral")
async def generate_referral(
    request: ReferralRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a unique referral link for a job posting."""
    service = get_social_service()
    link = service.generate_referral_link(request.job_id, current_user.id)
    return {"referral_link": link, "job_id": request.job_id}
