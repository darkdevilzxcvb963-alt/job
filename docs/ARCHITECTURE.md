# Architecture Documentation

## System Overview

The AI-Powered Resume & Job Matching Platform is a full-stack application that uses NLP and LLMs to intelligently match job seekers with job opportunities.

## Architecture Components

### 1. Frontend (React + Vite)
- **Location**: `frontend/`
- **Technology**: React 18, React Router, React Query
- **Purpose**: User interface for job seekers and recruiters
- **Key Features**:
  - Resume upload interface
  - Job posting form
  - Match visualization
  - Candidate and job management

### 2. Backend (FastAPI)
- **Location**: `backend/`
- **Technology**: FastAPI, SQLAlchemy, PostgreSQL
- **Purpose**: RESTful API for business logic and data processing
- **Key Components**:
  - API routes (`app/api/v1/`)
  - Database models (`app/models/`)
  - Business logic services (`app/services/`)
  - Configuration (`app/core/`)

### 3. Database (PostgreSQL)
- **Purpose**: Store candidates, jobs, and matches
- **Models**:
  - `Candidate`: Resume data and extracted information
  - `Job`: Job postings and requirements
  - `Match`: Matching scores and explanations

### 4. NLP Processing Pipeline
- **Components**:
  - Resume Parser: Extracts text from PDF/DOCX
  - NLP Processor: Text preprocessing, NER, skill extraction
  - Embedding Generator: Creates semantic vectors
  - Matching Engine: Computes similarity scores

### 5. LLM Integration
- **Purpose**: Generate summaries, normalize titles, explain matches
- **Service**: `app/services/llm_service.py`
- **Uses**: OpenAI API (configurable)

## Data Flow

1. **Resume Upload**:
   - User uploads resume → Backend parses file → Extract text → Generate embeddings → Store in database

2. **Job Posting**:
   - Recruiter posts job → Backend processes description → Generate embeddings → Normalize title → Store in database

3. **Matching**:
   - Calculate semantic similarity → Compute skill overlap → Check experience alignment → Generate overall score → Create LLM explanation → Store match

## API Endpoints

### Candidates
- `POST /api/v1/candidates` - Create candidate
- `GET /api/v1/candidates` - List candidates
- `GET /api/v1/candidates/{id}` - Get candidate
- `POST /api/v1/candidates/{id}/process-resume` - Process resume

### Jobs
- `POST /api/v1/jobs` - Create job
- `GET /api/v1/jobs` - List jobs
- `GET /api/v1/jobs/{id}` - Get job

### Matches
- `POST /api/v1/matches` - Create match
- `GET /api/v1/matches/candidate/{id}` - Get candidate matches
- `GET /api/v1/matches/job/{id}` - Get job matches

### Upload
- `POST /api/v1/upload/resume` - Upload resume file

## Security Considerations

- Environment variables for sensitive data
- File upload validation
- CORS configuration
- Input validation using Pydantic schemas

## Scalability

- Modular architecture for easy extension
- Database indexing on frequently queried fields
- Embedding caching (can be implemented)
- Async API endpoints for better performance
