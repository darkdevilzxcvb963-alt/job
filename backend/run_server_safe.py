#!/usr/bin/env python3
"""
Backend startup script with continuous retry logic
Ensures the backend stays running even if it crashes
"""
import subprocess
import sys
import time
from pathlib import Path

def run_backend():
    """Run the backend server"""
    venv_python = Path(__file__).parent / "venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print("ERROR: Virtual environment not found!")
        sys.exit(1)
    
    cmd = [
        str(venv_python),
        "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info"
    ]
    
    print("=" * 60)
    print("Starting Resume Matching Backend Server")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting server (attempt {retry_count + 1}/{max_retries})...")
            process = subprocess.Popen(cmd)
            return_code = process.wait()
            
            if return_code == 0:
                print("Server exited successfully")
                break
            else:
                print(f"Server exited with code {return_code}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying in 5 seconds... ({max_retries - retry_count} retries remaining)")
                    time.sleep(5)
        
        except KeyboardInterrupt:
            print("\nServer stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"Error running server: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(5)
    
    if retry_count >= max_retries:
        print(f"Failed to start server after {max_retries} attempts")
        sys.exit(1)

if __name__ == "__main__":
    run_backend()
