import pytest
from unittest.mock import MagicMock
from app.services.intelligence_service import IntelligenceService
from app.models.match import Match
from app.models.candidate import Candidate
from app.models.job import Job

class TestIntelligenceService:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_llm_service(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_db, mock_llm_service):
        return IntelligenceService(mock_db, mock_llm_service)

    def test_validate_skill_credibility(self, service):
        candidate = Candidate(
            skills=['Python', 'React', 'Cooking'],
            resume_text="I am a Python developer with experience in React UI."
        )
        job = Job(required_skills=['Python', 'React'])
        
        credibility = service._validate_skill_credibility(candidate, job)
        
        assert credibility.overall_credibility == 2/3
        assert 'Python' in credibility.validated_skills
        assert 'React' in credibility.validated_skills
        assert 'Cooking' in credibility.unsupported_skills

    def test_estimate_success_probability(self, mock_db, service):
        # Setup mocks
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        
        # Call 1: .query(Match).filter(...).count()
        mock_filter.count.return_value = 5
        # Call 2: .query(Match).count()
        mock_query.count.return_value = 10
        
        candidate = Candidate()
        job = Job()
        
        indicator = service._estimate_success_probability(candidate, job)
        
        assert indicator.score == 0.5
        assert indicator.status == "uncertain" # 10 < 50 threshold

    def test_audit_for_bias_flag(self, service):
        candidate = Candidate()
        job = Job()
        match = Match(skill_overlap_score=0.1, overall_score=0.9)
        
        audit = service._audit_for_bias(candidate, job, match)
        
        assert audit.is_biased is True
        assert audit.adjusted_score is not None
        assert audit.adjusted_score == 0.5 # (0.9 + 0.1) / 2
        assert "Potential inflation: High overall score despite low skill overlap." in audit.detected_patterns

    def test_audit_for_bias_clean(self, service):
        candidate = Candidate()
        job = Job()
        match = Match(skill_overlap_score=0.8, overall_score=0.85)
        
        audit = service._audit_for_bias(candidate, job, match)
        
        assert audit.is_biased is False
        assert len(audit.detected_patterns) == 0
