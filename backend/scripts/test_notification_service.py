
import asyncio
import os
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.notification_service import NotificationService
from app.core.config import settings

async def test_notifications():
    print("--- Notification Service Test ---")
    print(f"Using SMTP User: {settings.MAIL_USERNAME}")
    
    service = NotificationService()
    
    test_email = settings.MAIL_USERNAME # Send to self for testing
    
    print(f"\n1. Testing notify_recruiter_of_application to {test_email}...")
    success = await service.notify_recruiter_of_application(
        recruiter_email=test_email,
        recruiter_name="Test Recruiter",
        candidate_name="John Doe",
        job_title="Software Engineer",
        company="Tech Corp",
        cover_letter="I am very interested in this role because I love coding.",
        recruiter_phone="" # Skip SMS for now
    )
    
    if success:
        print("SUCCESS: Recruiter notification sent successfully!")
    else:
        print("FAILED: Recruiter notification FAILED!")

    print(f"\n2. Testing notify_candidate_of_application to {test_email}...")
    success = await service.notify_candidate_of_application(
        candidate_email=test_email,
        candidate_name="John Doe",
        job_title="Software Engineer",
        company="Tech Corp"
    )
    
    if success:
        print("SUCCESS: Candidate confirmation sent successfully!")
    else:
        print("FAILED: Candidate confirmation FAILED!")

if __name__ == "__main__":
    asyncio.run(test_notifications())
