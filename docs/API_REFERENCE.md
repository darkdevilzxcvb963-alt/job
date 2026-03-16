# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, the API does not require authentication. In production, implement JWT or OAuth2.

## Endpoints

### Candidates

#### Create Candidate
```http
POST /candidates
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "skills": null,
  "experience_years": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Get All Candidates
```http
GET /candidates?skip=0&limit=100
```

#### Get Candidate by ID
```http
GET /candidates/{candidate_id}
```

#### Process Resume
```http
POST /candidates/{candidate_id}/process-resume
Content-Type: application/json

{
  "file_path": "uploads/resume.pdf"
}
```

### Jobs

#### Create Job
```http
POST /jobs
Content-Type: application/json

{
  "title": "Software Engineer",
  "company": "Tech Corp",
  "description": "We are looking for...",
  "required_skills": ["Python", "React"],
  "experience_required": 3.0,
  "location": "San Francisco, CA"
}
```

#### Get All Jobs
```http
GET /jobs?skip=0&limit=100&active_only=true
```

#### Get Job by ID
```http
GET /jobs/{job_id}
```

### Matches

#### Create Match
```http
POST /matches?candidate_id=1&job_id=1
```

**Response:**
```json
{
  "id": 1,
  "candidate_id": 1,
  "job_id": 1,
  "semantic_similarity": 0.85,
  "skill_overlap_score": 0.75,
  "experience_alignment": 0.90,
  "overall_score": 0.83,
  "match_explanation": "This candidate is a strong match...",
  "created_at": "2024-01-01T00:00:00"
}
```

#### Get Candidate Matches
```http
GET /matches/candidate/{candidate_id}?limit=10
```

#### Get Job Matches
```http
GET /matches/job/{job_id}?limit=10
```

### Upload

#### Upload Resume
```http
POST /upload/resume
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "message": "File uploaded successfully",
  "file_path": "uploads/resume.pdf",
  "filename": "resume.pdf",
  "file_type": "pdf"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting
Currently not implemented. Consider adding rate limiting in production.

## Pagination
Use `skip` and `limit` query parameters for pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)
