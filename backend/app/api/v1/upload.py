"""
File Upload API Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
from app.core.config import settings

router = APIRouter()

@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file (PDF or DOCX)"""
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and DOCX files are allowed."
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = upload_dir / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return JSONResponse({
            "message": "File uploaded successfully",
            "file_path": str(file_path),
            "filename": file.filename,
            "file_type": file_ext[1:]  # Remove the dot
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )
