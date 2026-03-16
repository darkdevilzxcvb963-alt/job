import shutil
import os
import datetime
from pathlib import Path
from pathlib import Path

def backup_database():
    """Backup the SQLite database"""
    # Source database
    db_file = Path("backend/resume_matching.db")
    if not db_file.exists():
        print(f"Database not found at {db_file}")
        return

    # Backup directory
    backup_dir = Path("backend/backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Destination filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"resume_matching_{timestamp}.db"
    
    try:
        shutil.copy2(db_file, backup_file)
        print(f"✓ Database backed up successfully to: {backup_file}")
    except Exception as e:
        print(f"✗ Backup failed: {e}")

if __name__ == "__main__":
    # Ensure backend path is in sys.path if run directly
    import sys
    sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
    
    backup_database()
