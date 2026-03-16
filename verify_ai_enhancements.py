import sys
import os
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.nlp_processor import NLPProcessor
from app.services.matching_engine import MatchingEngine

def test_hierarchical_matching():
    print("--- Testing Hierarchical Skill Matching ---")
    engine = MatchingEngine()
    
    # Required: Django
    # Candidate has: Flask (Same category: Web Development -> Backend)
    job_skills = ["Django"]
    candidate_skills = ["Flask"]
    
    score = engine.calculate_skill_overlap(candidate_skills, job_skills)
    print(f"Match score (Django req, Flask present): {score:.2f}")
    assert 0.2 <= score <= 0.4, f"Expected partial credit (around 0.3), got {score}"
    
    # Required: Django
    # Candidate has: Python (Exact match if we use hierarchy extraction, but here we test raw scoring)
    candidate_skills_2 = ["Django"]
    score_2 = engine.calculate_skill_overlap(candidate_skills_2, job_skills)
    print(f"Match score (Django req, Django present): {score_2:.2f}")
    assert score_2 == 1.0, f"Expected 1.0, got {score_2}"
    print("Hierarchical matching test passed!")

def test_transferable_skills():
    print("\n--- Testing Transferable Skills Inference ---")
    processor = NLPProcessor()
    
    # Input text suggesting customer support role
    text = "Experience as a Customer Support representative handling high volume of calls."
    skills = processor.extract_skills(text)
    print(f"Extracted skills: {skills}")
    
    expected_inferred = ["Communication", "Problem Solving", "Empathy"]
    found_inferred = [s for s in expected_inferred if s in skills]
    print(f"Found inferred skills: {found_inferred}")
    
    assert len(found_inferred) > 0, "Expected at least some inferred skills"
    print("Transferable skills test passed!")

def test_experience_boost():
    print("\n--- Testing Experience Boost ---")
    engine = MatchingEngine()
    
    candidate_data = {
        "title": "Senior Software Engineer",
        "experience_years": 4,
        "skills": ["Python", "Django"]
    }
    
    job_data = {
        "title": "Senior Backend Developer",
        "experience_required": 5,
        "required_skills": ["Python", "Django"]
    }
    
    # 4 years vs 5 years required. 
    # Title match (Senior, Engineer/Developer overlap) should give relevance boost.
    scores = engine.match_candidate_to_job(candidate_data, job_data)
    print(f"Scores with boost: {scores}")
    
    # Without boost, 4/5 = 0.8
    # With 0.15 boost, 4 * 1.15 = 4.6. 4.6/5 = 0.92
    assert scores['experience_alignment'] > 0.8, f"Expected boost > 0.8, got {scores['experience_alignment']}"
    print("Experience boost test passed!")

if __name__ == "__main__":
    try:
        test_hierarchical_matching()
        test_transferable_skills()
        test_experience_boost()
        print("\nAll AI Enhancement tests PASSED!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
