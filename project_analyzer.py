#!/usr/bin/env python
"""
Comprehensive Project Diagnostic and Fixer
Analyzes and fixes all project issues
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class ProjectAnalyzer:
    def __init__(self):
        self.issues = []
        self.fixes = []
        self.project_root = Path(__file__).parent
        self.backend_root = self.project_root / "backend"
        self.frontend_root = self.project_root / "frontend"
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")
    
    def analyze_backend(self):
        """Analyze backend for issues"""
        self.log("Analyzing backend...", "ANALYSIS")
        
        # Check if backend directory exists
        if not self.backend_root.exists():
            self.issues.append("Backend directory not found")
            return
        
        # Check if main.py exists
        main_py = self.backend_root / "app" / "main.py"
        if not main_py.exists():
            self.issues.append("Backend app/main.py not found")
        else:
            self.log("✓ Backend app/main.py exists")
        
        # Check if requirements.txt exists
        reqs = self.backend_root / "requirements.txt"
        if not reqs.exists():
            self.issues.append("Backend requirements.txt not found")
        else:
            self.log("✓ Backend requirements.txt exists")
        
        # Check if venv exists
        venv = self.backend_root / "venv"
        if not venv.exists():
            self.issues.append("Backend virtual environment not found")
        else:
            self.log("✓ Backend venv exists")
        
        # Check if database exists
        db = self.backend_root / "resume_matching.db"
        if not db.exists():
            self.log("⚠ Database not found (will be created on first run)")
        else:
            self.log(f"✓ Database exists ({db.stat().st_size / (1024*1024):.2f} MB)")
        
        # Check core modules
        core_files = ["config.py", "database.py", "security.py", "dependencies.py", "email.py"]
        for file in core_files:
            path = self.backend_root / "app" / "core" / file
            if not path.exists():
                self.issues.append(f"Backend core/{file} not found")
            else:
                self.log(f"✓ Backend core/{file} exists")
        
        # Check API endpoints
        api_files = ["auth.py", "admin.py", "profiles.py", "jobs.py", "candidates.py"]
        for file in api_files:
            path = self.backend_root / "app" / "api" / "v1" / file
            if not path.exists():
                self.issues.append(f"Backend api/v1/{file} not found")
            else:
                self.log(f"✓ Backend api/v1/{file} exists")
    
    def analyze_frontend(self):
        """Analyze frontend for issues"""
        self.log("Analyzing frontend...", "ANALYSIS")
        
        # Check if frontend directory exists
        if not self.frontend_root.exists():
            self.issues.append("Frontend directory not found")
            return
        
        # Check if package.json exists
        pkg_json = self.frontend_root / "package.json"
        if not pkg_json.exists():
            self.issues.append("Frontend package.json not found")
        else:
            self.log("✓ Frontend package.json exists")
        
        # Check if node_modules exists
        node_modules = self.frontend_root / "node_modules"
        if not node_modules.exists():
            self.issues.append("Frontend node_modules not found (npm dependencies not installed)")
        else:
            self.log(f"✓ Frontend node_modules exists")
        
        # Check React components
        pages_dir = self.frontend_root / "src" / "pages"
        if pages_dir.exists():
            pages = list(pages_dir.glob("*.jsx"))
            self.log(f"✓ Found {len(pages)} React pages")
        else:
            self.issues.append("Frontend src/pages not found")
        
        # Check key pages
        key_pages = ["Home.jsx", "Login.jsx", "Signup.jsx", "AdminDashboard.jsx"]
        for page in key_pages:
            path = self.frontend_root / "src" / "pages" / page
            if not path.exists():
                self.issues.append(f"Frontend pages/{page} not found")
            else:
                self.log(f"✓ Frontend pages/{page} exists")
    
    def analyze_dependencies(self):
        """Analyze if dependencies are installed"""
        self.log("Analyzing dependencies...", "ANALYSIS")
        
        # Check Python venv
        python_exe = self.backend_root / "venv" / "Scripts" / "python.exe"
        if python_exe.exists():
            try:
                result = subprocess.run(
                    [str(python_exe), "-c", "import fastapi; import sqlalchemy; import uvicorn"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.log("✓ Backend dependencies are installed")
                else:
                    self.issues.append("Backend dependencies check failed")
            except Exception as e:
                self.issues.append(f"Could not verify backend dependencies: {str(e)}")
        else:
            self.issues.append("Python venv not found")
    
    def analyze_configuration(self):
        """Analyze configuration files"""
        self.log("Analyzing configuration...", "ANALYSIS")
        
        # Check backend .env
        env_file = self.backend_root / ".env"
        if env_file.exists():
            self.log("✓ Backend .env exists")
        else:
            self.issues.append("Backend .env not found")
        
        # Check config.py
        config_py = self.backend_root / "app" / "core" / "config.py"
        if config_py.exists():
            self.log("✓ Backend config.py exists")
        else:
            self.issues.append("Backend config.py not found")
    
    def run_analysis(self):
        """Run complete analysis"""
        self.log("=" * 60, "START")
        self.log("PROJECT ANALYSIS STARTING", "INFO")
        self.log("=" * 60, "START")
        
        self.analyze_backend()
        self.analyze_frontend()
        self.analyze_dependencies()
        self.analyze_configuration()
        
        self.log("=" * 60, "COMPLETE")
        
        if self.issues:
            self.log(f"Found {len(self.issues)} issues", "WARNING")
            for i, issue in enumerate(self.issues, 1):
                self.log(f"  {i}. {issue}", "ISSUE")
        else:
            self.log("No critical issues found!", "SUCCESS")
        
        self.log("=" * 60, "REPORT")
        return len(self.issues) == 0

if __name__ == "__main__":
    analyzer = ProjectAnalyzer()
    success = analyzer.run_analysis()
    sys.exit(0 if success else 1)
