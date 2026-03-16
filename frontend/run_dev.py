#!/usr/bin/env python3
"""
Frontend Dev Server Runner with Auto-Restart
Keeps the frontend running indefinitely with automatic restart on crash
"""
import subprocess
import sys
import time
import os
from pathlib import Path

# Get the frontend directory
frontend_dir = Path(__file__).parent.absolute()
os.chdir(frontend_dir)

print("\n" + "=" * 70)
print("Frontend Development Server (Persistent Runner)")
print("=" * 70)
print(f"Frontend directory: {frontend_dir}")
print(f"Server will be available at: http://localhost:3000")
print("=" * 70 + "\n")

def run_frontend():
    """Run the frontend with auto-restart on crash"""
    restart_count = 0
    
    while True:
        restart_count += 1
        try:
            print(f"\n[Run #{restart_count}] Starting Vite development server...")
            print("-" * 70)
            
            # Run npm run dev
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(line, end='', flush=True)
            
            # If we get here, the process exited
            returncode = process.wait()
            
            if returncode == 0:
                print("\n[INFO] Frontend exited normally")
            else:
                print(f"\n[WARNING] Frontend crashed with exit code {returncode}")
            
            # Wait before restart
            print(f"[AUTO-RESTART] Restarting in 3 seconds...")
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n[INFO] Frontend stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print(f"[AUTO-RESTART] Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    run_frontend()
