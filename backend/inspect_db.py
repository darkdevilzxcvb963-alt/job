from app.core.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match

def inspect_db():
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).all()
        print(f"Total Candidates: {len(candidates)}")
        for c in candidates:
            skills_type = type(c.skills).__name__
            has_embedding = c.resume_embedding is not None
            embedding_len = len(c.resume_embedding) if has_embedding else 0
            print(f"  Candidate: {c.name} ({c.email})")
            print(f"    Skills Type: {skills_type}")
            print(f"    Has Embedding: {has_embedding} (length: {embedding_len})")
            if skills_type == 'dict':
                total_skills = sum(len(v) for v in c.skills.values() if isinstance(v, list))
                print(f"    Total Skills (categorized): {total_skills}")
            elif skills_type == 'list':
                print(f"    Total Skills (flat): {len(c.skills)}")
        
        jobs = db.query(Job).all()
        print(f"\nTotal Jobs: {len(jobs)}")
        for j in jobs:
            has_embedding = j.job_embedding is not None
            embedding_len = len(j.job_embedding) if has_embedding else 0
            print(f"  Job: {j.title} at {j.company}")
            print(f"    Has Embedding: {has_embedding} (length: {embedding_len})")
            print(f"    Required Skills: {j.required_skills}")
            
        matches = db.query(Match).all()
        print(f"\nTotal Matches: {len(matches)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    inspect_db()
