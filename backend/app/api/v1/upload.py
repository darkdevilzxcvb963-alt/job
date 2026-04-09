"""
File Upload API Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import os
import shutil
import uuid
from pathlib import Path
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a resume file (PDF or DOCX)"""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and DOCX files are allowed."
        )
    
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Use UUID to avoid filename collisions
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return JSONResponse({
            "message": "File uploaded successfully",
            "file_path": str(file_path),
            "filename": unique_filename,
            "file_type": file_ext[1:]
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

@router.post("/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a profile picture and immediately save the URL to the user record"""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type. Only JPG, PNG and WebP are allowed."
        )
    
    upload_dir = Path(settings.UPLOAD_DIR) / "profiles"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Use UUID to avoid filename collisions between users
    unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Build the public URL (served via /uploads static mount)
        public_url = f"http://127.0.0.1:8001/uploads/profiles/{unique_filename}"
        
        # Immediately persist the URL to the user record
        current_user.profile_picture_url = public_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        return JSONResponse({
            "message": "Profile picture uploaded",
            "url": public_url
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )
