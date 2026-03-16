import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import Base, engine, get_db
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.core.dependencies import get_current_user

# Setup test database
@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def get_test_db():
        yield session
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_my_matches_with_intelligence(client, session):
    # 1. Create test user and candidate
    test_user = User(
        email="seeker@example.com", 
        full_name="Test Seeker", 
        role=UserRole.JOB_SEEKER,
        hashed_password="hashed_password_placeholder"
    )
    session.add(test_user)
    session.commit()
    
    candidate = Candidate(
        id="cand-1",
        email="seeker@example.com",
        name="Test Seeker",
        resume_text="Python Developer",
        skills=['Python']
    )
    session.add(candidate)
    
    # 2. Create test job
    job = Job(id="job-1", title="Python Dev", company="Tech Co", description="Test job description", required_skills=['Python'])
    session.add(job)
    
    # 3. Create match
    match = Match(
        id="match-1",
        candidate_id="cand-1",
        job_id="job-1",
        semantic_similarity=0.8,
        skill_overlap_score=0.9,
        experience_alignment=0.7,
        overall_score=0.8,
        status="matched"
    )
    session.add(match)
    session.commit()

    # Override current user
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    # 4. Call API
    response = client.get("/api/v1/matches/my-matches")
    
    # 5. Verify
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "intelligence" in data[0]
    intelligence = data[0]["intelligence"]
    assert "hiring_success_probability" in intelligence
    assert "skill_credibility" in intelligence
    assert intelligence["skill_credibility"]["overall_credibility"] == 1.0
