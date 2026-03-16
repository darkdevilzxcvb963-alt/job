"""
Tests for Matching Engine
"""
import pytest
import numpy as np
from app.services.matching_engine import MatchingEngine

def test_semantic_similarity():
    """Test semantic similarity calculation"""
    engine = MatchingEngine()
    
    # Test identical embeddings
    embedding1 = [0.1, 0.2, 0.3, 0.4]
    embedding2 = [0.1, 0.2, 0.3, 0.4]
    similarity = engine.calculate_semantic_similarity(embedding1, embedding2)
    assert similarity > 0.9  # Should be very similar
    
    # Test different embeddings
    embedding3 = [0.9, 0.8, 0.7, 0.6]
    similarity2 = engine.calculate_semantic_similarity(embedding1, embedding3)
    assert similarity2 < similarity  # Should be less similar

def test_skill_overlap():
    """Test skill overlap calculation"""
    engine = MatchingEngine()
    
    candidate_skills = ['Python', 'JavaScript', 'React', 'SQL']
    job_skills = ['Python', 'React', 'Node.js']
    
    overlap = engine.calculate_skill_overlap(candidate_skills, job_skills)
    assert 0 <= overlap <= 1
    assert overlap > 0  # Should have some overlap

def test_experience_alignment():
    """Test experience alignment calculation"""
    engine = MatchingEngine()
    
    # Candidate has more experience than required
    alignment = engine.calculate_experience_alignment(5.0, 3.0)
    assert alignment == 1.0
    
    # Candidate has less experience
    alignment2 = engine.calculate_experience_alignment(2.0, 5.0)
    assert 0 < alignment2 < 1.0
    
    # No experience required
    alignment3 = engine.calculate_experience_alignment(3.0, None)
    assert alignment3 == 1.0

def test_overall_score():
    """Test overall score calculation"""
    engine = MatchingEngine()
    
    score = engine.calculate_overall_score(
        semantic_sim=0.8,
        skill_overlap=0.7,
        exp_alignment=0.9
    )
    
    assert 0 <= score <= 1
    assert score > 0.5  # Should be a decent match
