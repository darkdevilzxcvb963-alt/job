import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.nlp_processor import NLPProcessor
from app.services.matching_engine import MatchingEngine
from app.core.config import settings

def test_skill_normalization():
    print("\n--- Testing Skill Normalization ---")
    nlp = NLPProcessor()
    
    # Test cases: (input_text, expected_canonical_skills)
    test_cases = [
        ("I am a Python (core) developer with ReactJS and AWS experience.", ["Python", "React", "AWS"]),
        ("Looking for JS, TS, and Golang experts.", ["JavaScript", "TypeScript", "Go"]),
        ("Deep Learning and NLP are my specialities.", ["Deep Learning", "Natural Language Processing"]),
        ("Experienced with k8s and ci/cd pipelines.", ["Kubernetes", "CI/CD"]),
    ]
    
    for text, expected in test_cases:
        skills = nlp.extract_skills(text)
        print(f"\nText: {text}")
        print(f"Extracted: {skills}")
        
        missing = [s for s in expected if s not in skills]
        if not missing:
            print("✅ PASS")
        else:
            print(f"❌ FAIL: Missing {missing}")

def test_matching_overlap():
    print("\n--- Testing Skill Matching Overlap ---")
    engine = MatchingEngine()
    
    # Candidate has "ReactJS", Job requires "React"
    candidate_skills = ["ReactJS", "Python (core)"]
    job_skills = ["React", "Python"]
    
    overlap = engine.calculate_skill_overlap(candidate_skills, job_skills)
    print(f"Candidate: {candidate_skills}")
    print(f"Job: {job_skills}")
    print(f"Overlap Score: {overlap:.2f}")
    
    if overlap == 1.0:
        print("✅ PASS: Synonyms correctly matched")
    else:
        print("❌ FAIL: Overlap should be 1.0")

    # Mismatch case
    candidate_skills = ["Java"]
    job_skills = ["Python"]
    overlap = engine.calculate_skill_overlap(candidate_skills, job_skills)
    print(f"\nCandidate: {candidate_skills}")
    print(f"Job: {job_skills}")
    print(f"Overlap Score: {overlap:.2f}")
    
    if overlap == 0.0:
        print("✅ PASS: Correctly identified no match")
    else:
        print("❌ FAIL: Overlap should be 0.0")

if __name__ == "__main__":
    try:
        test_skill_normalization()
        test_matching_overlap()
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
