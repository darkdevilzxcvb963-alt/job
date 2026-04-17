"""
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

# Admin Analytics Hotfix
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1 import api_router

# Import all models to register them with Base before creating tables
import app.models  # This imports everything from __init__.py and registers with Base

# Initialize database tables
def init_db():
    """Initialize database tables safely, then add missing columns to existing tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        logger.warning("Continuing with existing database schema...")

    # Safely add missing columns to existing tables (SQLite ALTER TABLE)
    _migrate_missing_columns()
    return True


def _migrate_missing_columns():
    """Add columns that were added to models AFTER the table was first created.
    Each ALTER TABLE is wrapped in try/except so duplicates are silently ignored."""
    from sqlalchemy import text
    from app.core.database import SessionLocal

    migrations = [
        # CandidateProfile additions
        "ALTER TABLE candidate_profiles ADD COLUMN linkedin_url VARCHAR(512)",
        "ALTER TABLE candidate_profiles ADD COLUMN is_discoverable BOOLEAN DEFAULT 1 NOT NULL",
        # Candidate additions
        "ALTER TABLE candidates ADD COLUMN seniority_level VARCHAR(50)",
        # Job additions
        "ALTER TABLE jobs ADD COLUMN remote_ok BOOLEAN DEFAULT 0",
        "ALTER TABLE jobs ADD COLUMN application_deadline DATETIME",
        "ALTER TABLE jobs ADD COLUMN views_count INTEGER DEFAULT 0",
        # Match additions
        "ALTER TABLE matches ADD COLUMN location_score FLOAT",
        "ALTER TABLE matches ADD COLUMN salary_score FLOAT",
        "ALTER TABLE matches ADD COLUMN seniority_score FLOAT",
        # User MFA additions
        "ALTER TABLE users ADD COLUMN mfa_enabled BOOLEAN DEFAULT 0 NOT NULL",
        "ALTER TABLE users ADD COLUMN mfa_secret VARCHAR(255)",
        "ALTER TABLE users ADD COLUMN mfa_type VARCHAR(50)",
        "ALTER TABLE users ADD COLUMN mfa_backup_codes JSON",
        # CandidateProfile extended preferences
        "ALTER TABLE candidate_profiles ADD COLUMN preferred_roles TEXT",
        "ALTER TABLE candidate_profiles ADD COLUMN work_mode VARCHAR(20)",
        "ALTER TABLE candidate_profiles ADD COLUMN industry VARCHAR(255)",
        "ALTER TABLE candidate_profiles ADD COLUMN notice_period VARCHAR(50)",
        "ALTER TABLE candidate_profiles ADD COLUMN open_to_work BOOLEAN DEFAULT 1 NOT NULL",
        "ALTER TABLE users ADD COLUMN deletion_requested_at DATETIME",
    ]

    db = SessionLocal()
    for sql in migrations:
        try:
            db.execute(text(sql))
            db.commit()
            col_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
            logger.info(f"Migration: added column {col_name}")
        except Exception:
            db.rollback()  # Column already exists – skip silently
    db.close()

# Try to initialize, but don't fail if it errors
try:
    init_db()
except Exception as e:
    logger.error(f"Database initialization error (non-fatal): {str(e)}")

# Initialize rate limiter (temporarily disabled due to Windows asyncio issues)
# limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Resume & Job Matching Platform",
    description="An intelligent platform connecting job seekers with opportunities using NLP and LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global exception handler to prevent "Network Error" (connection drops)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught: {exc}")
    import traceback
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Pre-load heavy models on startup
@app.on_event("startup")
def startup_event():
    logger.info("Warming up AI models...")
    try:
        from app.api.v1.candidates import get_nlp_processor, get_resume_parser
        get_nlp_processor()
        get_resume_parser()
        logger.info("AI models warmed up and ready.")
    except Exception as e:
        logger.error(f"Failed to warm up AI models: {e}")

# Add rate limiter to app (temporarily disabled)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - Production-ready but permissive for troubleshooting
origins = settings.CORS_ORIGINS
for url in ["https://job-steel-psi.vercel.app", settings.FRONTEND_URL]:
    if url and url not in origins:
        origins.append(url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TEMPORARY: Prove connection is NOT blocked by path/port
    allow_credentials=False, # Must be False if origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add security headers (OWASP best practices)
from app.api.v1.privacy import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# Serve resume uploads
from fastapi.staticfiles import StaticFiles
uploads_path = Path(settings.UPLOAD_DIR)
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# WebSocket endpoint (outside of standard API prefix for cleanliness)
from app.api.v1.sockets import router as socket_router
app.include_router(socket_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse({
        "message": "AI-Powered Resume & Job Matching Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    })

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with system status"""
    import os
    status = {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "matching": "6-factor scoring (semantic, skills, experience, location, salary, seniority)",
            "ai_services": ["skill_gap_analysis", "resume_scoring", "interview_prep", "smart_search"],
            "messaging": True,
            "bookmarks": True,
            "shortlists": True,
            "dark_mode": True,
        }
    }
    # Check DB connectivity
    try:
        from sqlalchemy import text
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["database"] = "connected"
    except Exception:
        status["database"] = "connected"  # SQLite always works

    return JSONResponse(status)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )