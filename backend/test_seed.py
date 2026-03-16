import sys
from pathlib import Path
import uuid

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.job import Job

print("Connecting to DB...")
db = SessionLocal()

print("Creating minimal job...")
print(f"DEBUG: Job class type: {type(Job)}")
try:
    print("DEBUG: Calling Job() constructor...")
    job = Job(
        title="Test Job",
        company="Test Company",
        description="Test Description"
    )
    print("Job object created.")
    db.add(job)
    print("Job added to session.")
    db.commit()
    print("✓ Job committed successfully!")
except BaseException as e:
    print(f"❌ Failed with {type(e)}: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
