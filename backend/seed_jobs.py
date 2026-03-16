import sys
import os
import uuid
from pathlib import Path

# Add backend to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("DEBUG: Starting seeding script...")

try:
    print("DEBUG: Importing SQLAlchemy core...")
    from app.core.database import SessionLocal, engine, Base, settings
    
    print("DEBUG: Importing all models to ensure registration...")
    from app.models.user import User
    from app.models.candidate import Candidate
    from app.models.job import Job
    from app.models.match import Match
    
    print("DEBUG: Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    print("DEBUG: Initializing NLP Processor...")
    from app.services.nlp_processor import NLPProcessor
    nlp = NLPProcessor(
        spacy_model=settings.SPACY_MODEL,
        embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
    )
    
    print("DEBUG: Connecting to DB...")
    db = SessionLocal()
    
    # Check if we already have jobs
    count = db.query(Job).count()
    if count > 0:
        print(f"DEBUG: Found {count} existing jobs. Skipping seeding.")
        db.close()
        sys.exit(0)

    jobs_to_seed = [
        {
            "title": "Senior Solutions Architect",
            "company": "Global Tech",
            "location": "Remote",
            "description": "Expert in AWS, distributed systems, and Python. Lead cloud-native transformations and mentoring engineering teams. Strong knowledge of cybersecurity and risk assessment.",
            "required_skills": ["Python", "AWS", "Cybersecurity", "Strategic Planning", "Technical Writing"],
            "experience_required": 8
        },
        {
            "title": "Frontend Developer",
            "company": "Visual Arts",
            "location": "Hybrid",
            "description": "Looking for a React expert with strong UI/UX design skills. Experience with Figma, Adobe Photoshop, and modern CSS frameworks. Collaborative team player with Agile experience.",
            "required_skills": ["React", "JavaScript", "Figma", "UI/UX Design", "Agile Methodology"],
            "experience_required": 3
        },
        {
            "title": "Business Developer",
            "company": "Growth Partners",
            "location": "Boston, MA",
            "description": "Drive business development through market research and competitive analysis. Excellent communication, negotiation, and client relations skills. Experience with Salesforce and HubSpot.",
            "required_skills": ["Business Development", "Market Research", "Negotiation", "Salesforce", "Public Speaking"],
            "experience_required": 5
        }
    ]

    print(f"DEBUG: Seeding {len(jobs_to_seed)} jobs...")
    for data in jobs_to_seed:
        print(f"DEBUG: Processing {data['title']}...")
        job = Job(
            title=data["title"],
            company=data["company"],
            location=data["location"],
            description=data["description"],
            experience_required=data["experience_required"],
            required_skills=data["required_skills"],
            is_active=True
        )
        
        # Generate embedding
        print("DEBUG: Generating embedding...")
        job.job_embedding = nlp.generate_embedding(data["description"])
        
        db.add(job)
        print("✓ Job added.")

    print("DEBUG: Committing...")
    db.commit()
    print("✓ Seeding complete!")
    db.close()

except BaseException as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
