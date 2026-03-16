#!/usr/bin/env python3
"""
AI-Powered Resume & Job Matching Platform - Setup Script
Cross-platform Python setup script
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, check=True, shell=False):
    """Run a shell command"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def check_command(command, name):
    """Check if a command is available"""
    try:
        run_command(command, check=False)
        print(f"[OK] {name} found")
        return True
    except:
        print(f"[X] {name} not found")
        return False

def setup_backend():
    """Set up the backend"""
    print("\n" + "="*50)
    print("Setting up backend...")
    print("="*50)
    
    backend_dir = Path("backend")
    os.chdir(backend_dir)
    
    # Create virtual environment
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating Python virtual environment...")
        run_command(f"{sys.executable} -m venv venv")
        print("[OK] Virtual environment created")
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate.bat"
        pip_command = "venv\\Scripts\\pip"
        python_command = "venv\\Scripts\\python"
    else:
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
        python_command = "venv/bin/python"
    
    # Install dependencies
    print("Installing Python dependencies (this may take a few minutes)...")
    run_command(f"{pip_command} install --upgrade pip", shell=True)
    run_command(f"{pip_command} install -r requirements.txt", shell=True)
    
    # Download SpaCy model
    print("Downloading SpaCy model...")
    run_command(f"{python_command} -m spacy download en_core_web_sm", shell=True)
    
    # Create .env file
    env_file = Path(".env")
    env_example = Path(".env.example")
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("[OK] .env file created")
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    os.chdir("..")
    print("[OK] Backend setup complete")

def setup_frontend():
    """Set up the frontend"""
    print("\n" + "="*50)
    print("Setting up frontend...")
    print("="*50)
    
    frontend_dir = Path("frontend")
    os.chdir(frontend_dir)
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies (this may take a few minutes)...")
    run_command("npm install")
    
    os.chdir("..")
    print("[OK] Frontend setup complete")

def main():
    """Main setup function"""
    print("="*50)
    print("AI-Powered Resume & Job Matching Platform")
    print("Automated Setup Script")
    print("="*50)
    
    # Check prerequisites
    print("\nChecking prerequisites...")
    python_ok = check_command("python --version", "Python")
    node_ok = check_command("node --version", "Node.js")
    docker_ok = check_command("docker --version", "Docker")
    
    if not python_ok:
        print("\n[X] Python is required. Please install Python 3.11+")
        sys.exit(1)
    
    if not node_ok:
        print("\n[X] Node.js is required. Please install Node.js 18+")
        sys.exit(1)
    
    # Setup backend and frontend
    setup_backend()
    setup_frontend()
    
    # Print next steps
    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit backend/.env and add your OpenAI API key (optional)")
    print("2. Set up PostgreSQL database")
    print("3. Run database migrations: cd backend && alembic upgrade head")
    print("4. Start backend: cd backend && uvicorn app.main:app --reload")
    print("5. Start frontend: cd frontend && npm run dev")
    print("\nOr use Docker Compose: docker-compose up -d")
    print("\nAccess the application:")
    print("  Frontend: http://localhost:3000")
    print("  Backend API: http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
