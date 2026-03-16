import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print(f"Python version: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path[:3]}")

try:
    print("Importing SessionLocal & Base...")
    from app.core.database import SessionLocal, Base, db_url
    print(f"Base ID: {id(Base)}")
    print(f"DB URL: {db_url}")
    
    print("Creating Session...")
    db = SessionLocal()
    print("✓ Session created.")
    
    print("Importing Job...")
    from app.models.job import Job
    print("✓ Job imported.")
    
    print("Creating Job instance...")
    job = Job(title="Test", company="Test", description="Test")
    print("✓ Job instance created.")
    
    print("Adding to session...")
    db.add(job)
    print("✓ Added to session.")
    
    db.close()
    print("✓ Session closed.")
    
except BaseException as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
