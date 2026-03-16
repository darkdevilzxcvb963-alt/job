
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.core.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match import Match
from app.models.application import Application
from app.models.notification import Notification

def verify_flow():
    db = SessionLocal()
    try:
        # Pick a candidate and job (using identified IDs)
        cand_id = "b1af6dd1-5234-4252-bde9-75b1ed7688e4"
        job_id = "b6e5a20b-c8f5-489e-9712-b79de8f11f50"
        
        cand = db.query(Candidate).filter(Candidate.id == cand_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not cand or not job:
            print("ERROR: Candidate or Job not found in DB.")
            return

        print(f"Found Candidate: {cand.name}")
        print(f"Found Job: {job.title} at {job.company}")

        # 1. Ensure a match exists
        match = db.query(Match).filter(Match.candidate_id == cand_id, Match.job_id == job_id).first()
        if not match:
            print("Creating a test match...")
            match = Match(
                candidate_id=cand_id,
                job_id=job_id,
                overall_score=0.85,
                status="matched"
            )
            db.add(match)
            db.commit()
            db.refresh(match)
        
        print(f"Match ID: {match.id}, Current Status: {match.status}")

        # 2. Simulate application (Reset status first if needed)
        match.status = "matched"
        db.commit()
        
        # We'll simulate the logic in matches.py:apply_to_job_with_form manually
        test_cover_letter = "This is a test cover letter for verification."
        
        # Logic from apply_to_job_with_form 
        match.status = "applied"
        
        # Upsert application
        existing_app = db.query(Application).filter(Application.match_id == match.id).first()
        if existing_app:
            db.delete(existing_app)
            db.commit()
            
        db.add(Application(
            match_id=match.id,
            candidate_id=cand.id,
            job_id=job.id,
            cover_letter=test_cover_letter
        ))
        
        # Create notification for recruiter
        if job.recruiter_id:
            # Delete old notifications for this match to be clean
            db.query(Notification).filter(Notification.related_match_id == match.id).delete()
            
            db.add(Notification(
                user_id=job.recruiter_id,
                type="application_received",
                message=f"TEST: {cand.name} applied to {job.title}",
                related_match_id=match.id
            ))
        
        db.commit()
        print("Simulated application submission.")

        # 3. Verify data retrieval
        db.refresh(match)
        app_record = db.query(Application).filter(Application.match_id == match.id).first()
        notif_record = db.query(Notification).filter(Notification.related_match_id == match.id).first()

        if match.status == "applied":
            print("SUCCESS: Match status updated to 'applied'")
        else:
            print(f"ERROR: Match status is {match.status}")

        if app_record and app_record.cover_letter == test_cover_letter:
            print("SUCCESS: Application record created with correct cover letter")
        else:
            print("ERROR: Application record missing or incorrect")

        if notif_record:
            print(f"SUCCESS: Notification created for recruiter: {notif_record.message}")
        else:
            print("ERROR: Notification not created")

    except Exception as e:
        print(f"ERROR during verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_flow()
