"""
Tests for NLP Processor
"""
import pytest
from app.services.nlp_processor import NLPProcessor

def test_preprocess_text():
    """Test text preprocessing"""
    processor = NLPProcessor()
    
    text = "Hello!!!   This is   a test."
    cleaned = processor.preprocess_text(text)
    assert "!!!" not in cleaned
    assert "   " not in cleaned

def test_extract_skills():
    """Test skill extraction"""
    processor = NLPProcessor()
    
    text = "I have experience with Python, React, and SQL databases."
    skills = processor.extract_skills(text)
    
    assert len(skills) > 0
    assert any('python' in skill.lower() for skill in skills)

def test_generate_embedding():
    """Test embedding generation"""
    processor = NLPProcessor()
    
    text = "Software engineer with 5 years of experience"
    embedding = processor.generate_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
