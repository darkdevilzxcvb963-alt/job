"""
Candidate API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from loguru import logger
from app.core.database import get_db, SessionLocal
from app.core.dependencies import get_current_user
from app.models.candidate import Candidate
from app.models.user import User, CandidateProfile
from app.schemas.candidate import CandidateCreate, CandidateResponse, CandidateUpdate, ProcessResumeRequest
from app.services.resume_parser import ResumeParser
from app.services.nlp_processor import NLPProcessor
from app.services.llm_service import LLMService
from app.services.matching_engine import MatchingEngine
from app.models.job import Job
from app.models.match import Match
from app.services.vector_store_service import vector_store
from app.core.config import settings
import os
import shutil
import re

router = APIRouter()

# Lazy-load these expensive services
_resume_parser = None
_nlp_processor = None
_llm_service = None

def get_resume_parser():
    global _resume_parser
    if _resume_parser is None:
        _resume_parser = ResumeParser()
    return _resume_parser

def get_nlp_processor():
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = NLPProcessor(
            spacy_model=settings.SPACY_MODEL,
            embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
        )
    return _nlp_processor

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

def generate_matches_task(candidate_id: str):
    """Background task to generate embeddings, summary and matches with its own DB session"""
    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate or not candidate.resume_text:
            return

        nlp_processor = get_nlp_processor()
        llm_service = get_llm_service()
        matching_engine = MatchingEngine()

        # Phase 1: Heavy AI work (Backgrounded)
        if not candidate.resume_embedding:
            logger.info(f"Generating embedding for candidate {candidate_id} in background")
            candidate.resume_embedding = nlp_processor.generate_embedding(candidate.resume_text)
        
        if not candidate.resume_summary:
            logger.info(f"Generating summary for candidate {candidate_id} in background")
            candidate.resume_summary = llm_service.summarize_resume(candidate.resume_text)
        
        db.commit()

        # Phase 2: Rapid numerical matching (Optimized with VectorStore)
        active_jobs = db.query(Job).filter(Job.is_active == True).all()
        
        # Build Vector Index for Jobs on the fly (or reuse if persistent)
        job_data_list = []
        for job in active_jobs:
            if job.job_embedding:
                job_data_list.append({"id": job.id, "embedding": job.job_embedding})
        
        vector_store.update_job_index(job_data_list)
        
        candidate_data = {
            "embedding": candidate.resume_embedding,
            "skills": candidate.skills or [].copy() if isinstance(candidate.skills, list) else candidate.skills or {},
            "experience_years": candidate.experience_years or 0
        }
        
        # Find similar jobs using spatial index
        similar_jobs = vector_store.find_similar_jobs(candidate.resume_embedding, top_k=50)
        
        match_results = []
        for sim in similar_jobs:
            job = db.query(Job).filter(Job.id == sim["id"]).first()
            if not job: continue
            
            existing_match = db.query(Match).filter(
                Match.candidate_id == candidate.id,
                Match.job_id == job.id
            ).first()
            if existing_match: continue
            
            job_data = {
                "embedding": job.job_embedding,
                "required_skills": job.required_skills or [],
                "experience_required": job.experience_required or 0,
                "title": job.title
            }
            
            scores = matching_engine.match_candidate_to_job(candidate_data, job_data)
            db_match = Match(
                candidate_id=candidate.id,
                job_id=job.id,
                **scores
            )
            db.add(db_match)
            match_results.append((db_match, scores, job_data))
        
        db.commit()
        
        db.commit()

        # Phase 3: Prioritized AI Explanations for Top 10
        match_results.sort(key=lambda x: x[1]["overall_score"], reverse=True)
        for db_match, scores, job_data in match_results[:10]:
            try:
                db_match.match_explanation = llm_service.generate_match_explanation(
                    candidate_data, job_data, scores
                )
            except Exception as e:
                logger.error(f"Error in background match explanation: {e}")
        
        db.commit()

        # Sync with CandidateProfile if available (ensures profile strength is updated)
        user = db.query(User).filter(User.email == candidate.email).first()
        if user and user.candidate_profile:
            user.candidate_profile.skills = candidate.skills
            # user.candidate_profile.headline = candidate.seniority_level  # Optional sync
            db.commit()
            logger.info(f"Synced Candidate data to CandidateProfile for {candidate.email}")
            
        logger.info(f"Background processing complete for candidate {candidate_id}")
        
    except Exception as e:
        logger.error(f"Error in background task for candidate {candidate_id}: {e}")
    finally:
        db.close()


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    """Create a new candidate"""
    # Check if candidate already exists
    db_candidate = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if db_candidate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate with this email already exists"
        )
    
    candidate_dict = candidate.dict()
    # Fallback to User.phone if candidate phone is missing
    if not candidate_dict.get("phone"):
        user = db.query(User).filter(User.email == candidate.email).first()
        if user and user.phone:
            candidate_dict["phone"] = user.phone
            
    db_candidate = Candidate(**candidate_dict)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@router.get("/", response_model=List[CandidateResponse])
async def get_candidates(
    email: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidates (filtered for recruiters to their own job matches if applicable)"""
    query = db.query(Candidate)
    
    # Filter by recruiter's job matches if not admin
    if current_user.role == "recruiter":
        # Only show candidates who have a match with one of the recruiter's jobs
        query = query.join(Match).join(Job).filter(Job.recruiter_id == current_user.id).distinct()
        
    if email:
        query = query.filter(Candidate.email == email)
        
    candidates = query.offset(skip).limit(limit).all()
    return candidates

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate

@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: str,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db)
):
    """Update a candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    update_data = candidate_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    db.commit()
    db.refresh(candidate)
    return candidate

@router.post("/{candidate_id}/process-resume")
def process_resume(
    candidate_id: str,
    request: ProcessResumeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process uploaded resume and extract information"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Parse resume
    resume_parser = get_resume_parser()
    nlp_processor = get_nlp_processor()
    llm_service = get_llm_service()
    
    # Extract file_path from request
    file_path = request.file_path
    
    # Resolve absolute path
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    resume_text = ""
    file_found = os.path.exists(file_path)
    
    if file_found:
        # File is on disk — parse it normally
        try:
            parsed_data = resume_parser.parse(file_path)
            if "error" in parsed_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=parsed_data["error"]
                )
            resume_text = parsed_data.get("text", "")
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Could not parse file {file_path}: {e}")
            resume_text = ""
    
    # Fallback: use stored resume_text from database if file is missing or empty
    if not resume_text or len(resume_text.strip()) == 0:
        if candidate.resume_text and len(candidate.resume_text.strip()) > 0:
            resume_text = candidate.resume_text
            logger.info(f"Using stored resume_text for candidate {candidate.name} (file not on disk)")
        else:
            logger.warning(f"No resume text available for {candidate.name} — file missing and no stored text")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resume file not found at {file_path} and no stored resume text available. Please re-upload the resume."
            )
        
    try:
        # Extract skills and entities
        if not resume_text or len(resume_text.strip()) == 0:
            logger.warning(f"Constructed empty text for candidate {candidate.name}. Is it a scanned PDF?")
            # Do NOT raise exception, let the frontend handle the warning
            categorized_skills = {cat: [] for cat in nlp_processor.skill_keywords.keys()} if hasattr(nlp_processor, 'skill_keywords') else {}
        else:
            categorized_skills = nlp_processor.extract_skills_categorized(resume_text)
            
            # Fallback to LLM if local extraction finds nothing but text is present
            total_skills = sum(len(skills) for skills in categorized_skills.values())
            if total_skills == 0 and len(resume_text.strip()) > 50:
                logger.info(f"Local NLP found 0 skills for {candidate.name}. Falling back to LLM extraction.")
                llm_skills = llm_service.extract_skills_categorized(resume_text)
                if any(len(s) > 0 for s in llm_skills.values()):
                    categorized_skills = llm_skills
                    logger.info(f"LLM successfully extracted {sum(len(s) for s in llm_skills.values())} skills as fallback.")
        
        # Organize resume file into candidate-specific folder (only if file exists)
        final_file_path = file_path
        if file_found:
            try:
                safe_name = re.sub(r'[^\w\s-]', '', candidate.name).strip()
                safe_name = re.sub(r'[-\s]+', '_', safe_name)
                
                candidate_dir = os.path.join(settings.UPLOAD_DIR, safe_name)
                os.makedirs(candidate_dir, exist_ok=True)
                
                filename = os.path.basename(file_path)
                new_path = os.path.join(candidate_dir, filename)
                
                if os.path.abspath(file_path) != os.path.abspath(new_path):
                    shutil.move(file_path, new_path)
                    final_file_path = new_path
                    logger.info(f"Moved resume for {candidate.name} to {new_path}")
            except Exception as move_err:
                logger.warning(f"Could not organize resume file into subfolder: {move_err}")
            
        # Store metadata
        candidate.skills = categorized_skills
        candidate.resume_text = resume_text
        if file_found:
            candidate.resume_file_path = final_file_path
            candidate.resume_file_type = parsed_data.get("file_type", "unknown") if file_found else candidate.resume_file_type
        
        db.commit()
        db.refresh(candidate)
        
        # Trigger background task for embeddings, summary and matches
        background_tasks.add_task(generate_matches_task, candidate.id)
        
        # Calculate total skills across all categories
        total_skills = sum(len(skills) for skills in categorized_skills.values())
        
        all_skills_flat = []
        for category_skills in categorized_skills.values():
            all_skills_flat.extend(category_skills)
        
        return {
            "message": "Resume processed successfully. AI analysis and matches will appear shortly.",
            "skills_extracted": total_skills,
            "skills": all_skills_flat,
            "skills_by_category": categorized_skills,
            "summary": "Generating in background...",
            "debug_text_len": len(resume_text),
            "file_path": final_file_path,
            "extraction_method": parsed_data.get("extraction_method", "unknown") if file_found else "database",
            "warning": parsed_data.get("warning") if file_found else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing resume for {candidate.name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume content: {str(e)}"
        )
@router.post("/{candidate_id}/resume")
async def upload_and_analyze_resume(
    candidate_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Upload and analyze resume in a single step.
    Saves the file and immediately attempts extraction.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
        
    # Validation
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and DOCX files are allowed."
        )

    # 1. Save File
    safe_name = re.sub(r'[^\w\s-]', '', candidate.name).strip()
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    candidate_dir = os.path.join(settings.UPLOAD_DIR, safe_name)
    os.makedirs(candidate_dir, exist_ok=True)
    
    filename = file.filename
    file_path = os.path.join(candidate_dir, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save resume file")

    # 2. Parse & Analyze
    try:
        resume_parser = get_resume_parser()
        nlp_processor = get_nlp_processor()
        
        parsed_data = resume_parser.parse(file_path)
        if "error" in parsed_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=parsed_data["error"]
            )
        resume_text = parsed_data.get("text", "")
        
        file_size = os.path.getsize(file_path)
        logger.info(f"Uploaded file: {file_path}, Size: {file_size} bytes, Extracted Text Length: {len(resume_text)}")
        
        if not resume_text or len(resume_text.strip()) == 0:
             logger.warning(f"Constructed empty text for {file_path}. Is it a scanned PDF?")
             # Do NOT raise exception, let the frontend handle the warning
             # raise HTTPException(status_code=400, detail="Could not extract text from resume.")
             
        categorized_skills = nlp_processor.extract_skills_categorized(resume_text)
        
        # Fallback to LLM if local extraction finds nothing but text is present
        total_skills_local = sum(len(skills) for skills in categorized_skills.values())
        if total_skills_local == 0 and len(resume_text.strip()) > 50:
            logger.info(f"Local NLP found 0 skills for {candidate.name}. Falling back to LLM extraction.")
            llm_service = get_llm_service()
            llm_skills = llm_service.extract_skills_categorized(resume_text)
            if any(len(s) > 0 for s in llm_skills.values()):
                categorized_skills = llm_skills
                logger.info(f"LLM successfully extracted {sum(len(s) for s in llm_skills.values())} skills as fallback.")
        
        # 3. Update Candidate
        candidate.skills = categorized_skills
        candidate.resume_text = resume_text
        candidate.resume_file_path = file_path
        candidate.resume_file_type = parsed_data.get("file_type", "unknown")
        
        db.commit()
        db.refresh(candidate)
        
        # 4. Background Tasks
        if background_tasks:
            background_tasks.add_task(generate_matches_task, candidate.id)

        # 5. Return Result
        total_skills = sum(len(skills) for skills in categorized_skills.values())
        all_skills_flat = []
        for category_skills in categorized_skills.values():
            all_skills_flat.extend(category_skills)
            
        return {
            "message": "Resume uploaded and analyzed successfully.",
            "skills_extracted": total_skills,
            "skills": all_skills_flat,
            "skills_by_category": categorized_skills,
            "debug_text_len": len(resume_text),
            "extraction_method": parsed_data.get("extraction_method", "unknown"),
            "file_path": file_path,
            "warning": parsed_data.get("warning")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        # Even if analysis fails, we saved the file, so we could technically return success with warning,
        # but the user wants analysis. So we return error.
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")
