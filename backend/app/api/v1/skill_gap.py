"""
Skill Gap Analysis API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.skill_gap import SkillGapAnalysis
from app.services.skill_gap_service import SkillGapService
from app.services.llm_service import LLMService
from app.schemas.features import SkillGapResponse, SkillGapMissing, SkillGapBridgeable, SkillGapRecommendation

router = APIRouter()


@router.get("/{candidate_id}/{job_id}", response_model=SkillGapResponse)
async def analyze_skill_gap(
    candidate_id: str,
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze skill gap between a candidate and a job"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Perform analysis
    service = SkillGapService(LLMService())
    gap = service.analyze_gap(
        candidate.skills,
        job.required_skills or [],
        job.preferred_skills or []
    )
    
    # Generate recommendations
    recommendations = service.generate_recommendations(gap)
    
    # Store results
    analysis = SkillGapAnalysis(
        candidate_id=candidate_id,
        job_id=job_id,
        missing_skills=[m['skill'] for m in gap['missing_skills']],
        matched_skills=gap['matched_skills'],
        bridgeable_skills=gap['bridgeable_skills'],
        recommendations=recommendations,
        coverage_score=gap['coverage_score']
    )
    db.add(analysis)
    db.commit()
    
    return SkillGapResponse(
        coverage_score=gap['coverage_score'],
        matched_skills=gap['matched_skills'],
        missing_skills=[SkillGapMissing(**m) for m in gap['missing_skills']],
        bridgeable_skills=[SkillGapBridgeable(**b) for b in gap['bridgeable_skills']],
        recommendations=[SkillGapRecommendation(**r) for r in recommendations],
        total_required=gap['total_required'],
        total_matched=gap['total_matched']
    )
