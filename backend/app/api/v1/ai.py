"""
AI Assistant API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from itertools import islice
import numpy as np
from loguru import logger

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.services.llm_service import LLMService
from app.services.nlp_processor import NLPProcessor
from app.schemas.ai import (
    OutreachRequest, OutreachResponse,
    JDGenRequest, JDGenResponse,
    InterviewPrepRequest, InterviewPrepResponse,
    SmartSearchRequest, SmartSearchResponse, SmartSearchCandidate
)
from app.schemas.ai_trainer import TrainingRequest, TrainingResponse
from app.core.config import settings

router = APIRouter()

# Lazy-load services
_llm_service = None
_nlp_processor = None
_ai_trainer_service = None

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

def get_nlp_processor():
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = NLPProcessor(
            spacy_model=settings.SPACY_MODEL,
            embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
        )
    return _nlp_processor

def get_ai_trainer_service():
    global _ai_trainer_service
    if _ai_trainer_service is None:
        from app.services.ai_trainer_service import AITrainerService
        _ai_trainer_service = AITrainerService()
    return _ai_trainer_service

@router.post("/generate-outreach", response_model=OutreachResponse)
async def generate_outreach(
    request: OutreachRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate a personalized outreach message (Recruiter only)"""
    # Personalization logic
    if current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only recruiters can generate outreach messages")
    
    message = llm_service.generate_outreach_message(
        request.candidate_name, request.job_title, request.company, request.match_explanation
    )
    return {"message": message}

@router.post("/generate-jd", response_model=JDGenResponse)
async def generate_jd(
    request: JDGenRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate a job description from points (Recruiter only)"""
    if current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only recruiters can generate job descriptions")
    
    jd = llm_service.generate_job_description(request.title, request.key_points)
    return {"job_description": jd}

@router.post("/generate-interview-prep", response_model=InterviewPrepResponse)
async def generate_interview_prep(
    request: InterviewPrepRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate interview practice questions (Candidate only)"""
    # Candidates should be able to prep for their matches
    questions = llm_service.generate_interview_questions(
        request.candidate_skills, request.job_requirements, request.job_title
    )
    return {"questions": questions}

@router.post("/smart-search", response_model=SmartSearchResponse)
async def smart_search(
    request: SmartSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    nlp_processor: NLPProcessor = Depends(get_nlp_processor)
):
    """Search candidates using natural language embeddings (Recruiter only)"""
    if current_user.role != UserRole.RECRUITER.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only recruiters can use smart search")
    
    # Generate query embedding
    query_embedding = nlp_processor.generate_embedding(request.query)
    
    # Get all candidates with embeddings
    candidates = db.query(Candidate).filter(Candidate.resume_embedding != None).all()
    
    results = []
    for candidate in candidates:
        # Calculate cosine similarity
        cand_embedding = np.array(candidate.resume_embedding)
        norm_q = np.linalg.norm(query_embedding)
        norm_c = np.linalg.norm(cand_embedding)
        
        if norm_q > 0 and norm_c > 0:
            score = np.dot(query_embedding, cand_embedding) / (norm_q * norm_c)
        else:
            score = 0
            
        # Ensure skills matches schema (Dict[str, List[str]])
        candidate_skills = candidate.skills
        if isinstance(candidate_skills, list):
            candidate_skills = {"General": candidate_skills}

        # We use a lower threshold for "search" vs "matching"
        if score > 0.3:
            results.append(SmartSearchCandidate(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                score=float(score),
                skills=candidate_skills,
                experience_years=candidate.experience_years,
                summary=candidate.resume_summary
            ))
            
    # Sort by score
    results.sort(key=lambda x: x.score, reverse=True)
    
    # Use islice as a workaround for linter quirk with standard slicing
    slice_limit = int(request.limit) if request.limit else 10
    final_results = list(islice(results, slice_limit))
    return {"results": final_results}


@router.post("/score-resume")
async def score_resume(
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Score a candidate's resume for ATS compatibility and quality"""
    from app.services.resume_scorer import ResumeScorer
    from app.models.job import Job

    # Find candidate
    candidate = None
    if candidate_id:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    else:
        candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()

    if not candidate or not candidate.resume_text:
        raise HTTPException(status_code=404, detail="No resume found. Please upload a resume first.")

    target_skills = None
    if job_id:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job and job.required_skills:
            target_skills = job.required_skills

    scorer = ResumeScorer()
    result = scorer.score_resume(candidate.resume_text, target_skills)

    return result

@router.post("/generate-training", response_model=TrainingResponse)
async def generate_training(
    request: TrainingRequest,
    current_user: User = Depends(get_current_user),
    ai_trainer: Any = Depends(get_ai_trainer_service)
):
    """
    Generate structured AI training, skills gap analysis, and questions 
    based on the master Ollama prompt.
    """
    try:
        response_data = await ai_trainer.generate_training_plan(
            job_role=request.job_role,
            candidate_skills=request.candidate_skills,
            required_skills=request.job_skills,  # map job_skills to required_skills
            matched_skills=request.matched_skills,
            question=request.question,
            answer=request.answer
        )
        return response_data
    except Exception as e:
        logger.error(f"Error generating training plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
