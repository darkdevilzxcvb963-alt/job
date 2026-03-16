#!/usr/bin/env python
"""
Simple script to run the FastAPI server with proper asyncio configuration for Windows
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Starting Resume Matching Platform Backend Server")
    print("="*70)
    print(f"Backend directory: {backend_dir}")
    print(f"Database: {backend_dir}/resume_matching.db")
    print(f"Server will be available at: http://127.0.0.1:8000")
    print(f"API Docs: http://127.0.0.1:8000/docs")
    print("="*70 + "\n")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
