"""
Database Configuration and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Database URL from settings
db_url = settings.DATABASE_URL

# Ensure persistence for SQLite
if "sqlite" in db_url:
    # Handle both relative and absolute paths
    db_path = db_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Ensure backup directory exists
    backup_dir = os.path.abspath(settings.DB_BACKUP_DIR)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)

# Create database engine
if "sqlite" in db_url:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
    # Debug: List tables and file info to a file
    from sqlalchemy import inspect
    import os
    inspector = inspect(engine)
    db_file_path = db_url.replace("sqlite:///", "")
    with open("server_startup_debug.log", "w") as f:
        f.write(f"DEBUG: DATABASE_URL is {db_url}\n")
        if os.path.exists(db_file_path):
            f.write(f"DEBUG: DB File Exists at {os.path.abspath(db_file_path)}\n")
            f.write(f"DEBUG: DB File Size: {os.path.getsize(db_file_path)}\n")
            f.write(f"DEBUG: DB File Mtime: {os.path.getmtime(db_file_path)}\n")
            try:
                user_columns = [col['name'] for col in inspector.get_columns('users')]
                f.write(f"DEBUG: 'users' table columns: {user_columns}\n")
            except Exception as e:
                f.write(f"DEBUG: Error inspecting 'users' table: {e}\n")
        else:
            f.write(f"DEBUG: DB File DOES NOT EXIST at {db_file_path}\n")
        f.write(f"DEBUG: Tables in database: {inspector.get_table_names()}\n")
    print(f"DEBUG: Startup info written to server_startup_debug.log")
else:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
