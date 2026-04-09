"""
Profile Settings API — CRUD for Experience, Education, Projects,
Certifications, Job Preferences, AI Settings, Notifications, Privacy,
and Profile Strength calculation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, CandidateProfile
from app.models.profile_settings import (
    UserExperience, UserEducation, UserProject, UserCertification,
    AISettings, NotificationPreferences, PrivacySettings, UserActivityLog,
)
from app.schemas.profile_settings import (
    ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    EducationCreate, EducationUpdate, EducationResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    CertificationCreate, CertificationUpdate, CertificationResponse,
    JobPreferencesUpdate, JobPreferencesResponse,
    AISettingsUpdate, AISettingsResponse,
    NotificationPreferencesUpdate, NotificationPreferencesResponse,
    PrivacySettingsUpdate, PrivacySettingsResponse,
    ProfileStrengthResponse,
)
from loguru import logger

router = APIRouter(prefix="/settings", tags=["profile-settings"])


# ═══════════════════════════════════════════════════════════════════════════════
#  EXPERIENCE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/experience", response_model=List[ExperienceResponse])
async def list_experiences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(UserExperience).filter(
        UserExperience.user_id == current_user.id
    ).order_by(UserExperience.start_date.desc()).all()


@router.post("/experience", response_model=ExperienceResponse, status_code=201)
async def add_experience(
    data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = UserExperience(user_id=current_user.id, **data.dict())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.put("/experience/{exp_id}", response_model=ExperienceResponse)
async def update_experience(
    exp_id: str,
    data: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(UserExperience).filter(
        UserExperience.id == exp_id, UserExperience.user_id == current_user.id
    ).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(exp, k, v)
    exp.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/experience/{exp_id}", status_code=204)
async def delete_experience(
    exp_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.query(UserExperience).filter(
        UserExperience.id == exp_id, UserExperience.user_id == current_user.id
    ).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    db.delete(exp)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  EDUCATION
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/education", response_model=List[EducationResponse])
async def list_education(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(UserEducation).filter(
        UserEducation.user_id == current_user.id
    ).order_by(UserEducation.end_year.desc()).all()


@router.post("/education", response_model=EducationResponse, status_code=201)
async def add_education(
    data: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    edu = UserEducation(user_id=current_user.id, **data.dict())
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return edu


@router.put("/education/{edu_id}", response_model=EducationResponse)
async def update_education(
    edu_id: str,
    data: EducationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    edu = db.query(UserEducation).filter(
        UserEducation.id == edu_id, UserEducation.user_id == current_user.id
    ).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(edu, k, v)
    edu.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(edu)
    return edu


@router.delete("/education/{edu_id}", status_code=204)
async def delete_education(
    edu_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    edu = db.query(UserEducation).filter(
        UserEducation.id == edu_id, UserEducation.user_id == current_user.id
    ).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    db.delete(edu)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(UserProject).filter(
        UserProject.user_id == current_user.id
    ).order_by(UserProject.created_at.desc()).all()


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def add_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proj = UserProject(user_id=current_user.id, **data.dict())
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.put("/projects/{proj_id}", response_model=ProjectResponse)
async def update_project(
    proj_id: str,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proj = db.query(UserProject).filter(
        UserProject.id == proj_id, UserProject.user_id == current_user.id
    ).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(proj, k, v)
    proj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(proj)
    return proj


@router.delete("/projects/{proj_id}", status_code=204)
async def delete_project(
    proj_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proj = db.query(UserProject).filter(
        UserProject.id == proj_id, UserProject.user_id == current_user.id
    ).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(proj)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  CERTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/certifications", response_model=List[CertificationResponse])
async def list_certifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(UserCertification).filter(
        UserCertification.user_id == current_user.id
    ).order_by(UserCertification.issue_date.desc()).all()


@router.post("/certifications", response_model=CertificationResponse, status_code=201)
async def add_certification(
    data: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cert = UserCertification(user_id=current_user.id, **data.dict())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.put("/certifications/{cert_id}", response_model=CertificationResponse)
async def update_certification(
    cert_id: str,
    data: CertificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cert = db.query(UserCertification).filter(
        UserCertification.id == cert_id, UserCertification.user_id == current_user.id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(cert, k, v)
    cert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(cert)
    return cert


@router.delete("/certifications/{cert_id}", status_code=204)
async def delete_certification(
    cert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cert = db.query(UserCertification).filter(
        UserCertification.id == cert_id, UserCertification.user_id == current_user.id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    db.delete(cert)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  JOB PREFERENCES
# ═══════════════════════════════════════════════════════════════════════════════

def _ensure_candidate_profile(user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _safe_json_load(val):
    if val is None:
        return None
    if isinstance(val, list):
        return val
    try:
        return json.loads(val)
    except Exception:
        return None


@router.get("/preferences", response_model=JobPreferencesResponse)
async def get_job_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = _ensure_candidate_profile(current_user, db)
    return p


@router.put("/preferences", response_model=JobPreferencesResponse)
async def update_job_preferences(
    data: JobPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = _ensure_candidate_profile(current_user, db)
    if data.headline is not None:
        p.headline = data.headline
    if data.skills is not None:
        p.skills = data.skills
    if data.preferred_roles is not None:
        p.preferred_roles = data.preferred_roles
    if data.preferred_locations is not None:
        p.preferred_locations = data.preferred_locations
    if data.preferred_job_types is not None:
        p.preferred_job_types = data.preferred_job_types
    if data.salary_expectation_min is not None:
        p.salary_expectation_min = data.salary_expectation_min
    if data.salary_expectation_max is not None:
        p.salary_expectation_max = data.salary_expectation_max
    if data.work_mode is not None:
        p.work_mode = data.work_mode
    if data.industry is not None:
        p.industry = data.industry
    if data.notice_period is not None:
        p.notice_period = data.notice_period
    if data.open_to_work is not None:
        p.open_to_work = data.open_to_work
    p.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(p)
    return p


# ═══════════════════════════════════════════════════════════════════════════════
#  AI SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/ai", response_model=AISettingsResponse)
async def get_ai_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
    if not s:
        return AISettingsResponse()
    return s


@router.put("/ai", response_model=AISettingsResponse)
async def update_ai_settings(
    data: AISettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
    if not s:
        s = AISettings(user_id=current_user.id)
        db.add(s)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(s, k, v)
    s.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(s)
    return s


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTIFICATION PREFERENCES
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/notifications", response_model=NotificationPreferencesResponse)
async def get_notification_prefs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(NotificationPreferences).filter(
        NotificationPreferences.user_id == current_user.id
    ).first()
    if not n:
        return NotificationPreferencesResponse()
    return n


@router.put("/notifications", response_model=NotificationPreferencesResponse)
async def update_notification_prefs(
    data: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(NotificationPreferences).filter(
        NotificationPreferences.user_id == current_user.id
    ).first()
    if not n:
        n = NotificationPreferences(user_id=current_user.id)
        db.add(n)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(n, k, v)
    n.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(n)
    return n


# ═══════════════════════════════════════════════════════════════════════════════
#  PRIVACY SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/privacy", response_model=PrivacySettingsResponse)
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ps = db.query(PrivacySettings).filter(
        PrivacySettings.user_id == current_user.id
    ).first()
    if not ps:
        return PrivacySettingsResponse()
    return ps


@router.put("/privacy", response_model=PrivacySettingsResponse)
async def update_privacy_settings(
    data: PrivacySettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ps = db.query(PrivacySettings).filter(
        PrivacySettings.user_id == current_user.id
    ).first()
    if not ps:
        ps = PrivacySettings(user_id=current_user.id)
        db.add(ps)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(ps, k, v)
    ps.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ps)
    return ps


# ═══════════════════════════════════════════════════════════════════════════════
#  PROFILE STRENGTH
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/profile-strength", response_model=ProfileStrengthResponse)
async def get_profile_strength(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    completed = []
    missing = []
    suggestions = []

    # Basic info
    if current_user.full_name:
        completed.append("Full Name")
    else:
        missing.append("Full Name"); suggestions.append("Add your full name to appear in recruiter searches")

    if current_user.bio:
        completed.append("Bio")
    else:
        missing.append("Bio"); suggestions.append("Write a short bio to introduce yourself")

    if current_user.profile_picture_url:
        completed.append("Profile Photo")
    else:
        missing.append("Profile Photo"); suggestions.append("Upload a professional photo to increase profile views by up to 36%")

    if current_user.phone:
        completed.append("Phone Number")
    else:
        missing.append("Phone Number"); suggestions.append("Add a phone number for recruiter contact")

    # Candidate profile
    cp = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if cp:
        if cp.headline:
            completed.append("Headline")
        else:
            missing.append("Headline"); suggestions.append("Add a professional headline (e.g. 'Senior Python Developer')")

        if cp.skills:
            completed.append("Skills")
        else:
            missing.append("Skills"); suggestions.append("Add your top skills to improve AI match accuracy")

        if cp.preferred_locations:
            completed.append("Preferred Locations")
        else:
            missing.append("Preferred Locations"); suggestions.append("Set location preferences for better job matches")
    else:
        missing.extend(["Headline", "Skills", "Preferred Locations"])
        suggestions.append("Complete your candidate profile to start receiving AI matches")

    # Experience
    exp_count = db.query(UserExperience).filter(UserExperience.user_id == current_user.id).count()
    if exp_count > 0:
        completed.append("Experience")
    else:
        missing.append("Experience"); suggestions.append("Add at least one work experience entry")

    # Education
    edu_count = db.query(UserEducation).filter(UserEducation.user_id == current_user.id).count()
    if edu_count > 0:
        completed.append("Education")
    else:
        missing.append("Education"); suggestions.append("Add your education details")

    # Projects
    proj_count = db.query(UserProject).filter(UserProject.user_id == current_user.id).count()
    if proj_count > 0:
        completed.append("Projects")
    else:
        missing.append("Projects"); suggestions.append("Showcase your projects to stand out to recruiters")

    # Resume
    from app.models.candidate import Candidate
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if candidate and candidate.resume_text:
        completed.append("Resume")
    else:
        missing.append("Resume"); suggestions.append("Upload your resume for AI-powered skill extraction")

    total = len(completed) + len(missing)
    percentage = round((len(completed) / total) * 100, 1) if total > 0 else 0

    return ProfileStrengthResponse(
        percentage=percentage,
        completed=completed,
        missing=missing,
        suggestions=suggestions[:5],  # Top 5 suggestions
    )
