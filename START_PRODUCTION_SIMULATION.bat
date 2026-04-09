@echo off
echo ========================================================
echo 🚀 PRODUCTION DEPLOYMENT SIMULATOR (1000%% WORKING CHECK)
echo ========================================================
echo.
echo Running your application in strict Production Mode on your laptop
echo to ensure all Databases, APIs, Resume Matchers function flawlessly!
echo.

set ENVIRONMENT=production
set SECRET_KEY=super_secure_production_test_key_123
set CORS_ORIGINS_STR=http://localhost:3000

echo [1/3] Verifying PostgreSQL / SQLite production handlers...
python backend/check_db_state.py
if %errorlevel% neq 0 (
    echo [ERROR] Database validation failed.
    pause
    exit /b %errorlevel%
)
echo.

echo [2/3] Verifying NLP Resume Parser and Matcher in Production Mode...
python backend/test_full_pipeline.py
if %errorlevel% neq 0 (
    echo [ERROR] AI Pipeline validation failed.
    pause
    exit /b %errorlevel%
)
echo.

echo [3/3] System successfully verified for deployment! 
echo.
echo ========================================================
echo 🎯 STARTING PRODUCTION BACKEND AND FRONTEND...
echo ========================================================
echo Please visit: http://localhost:3000 to see it live!
echo.

start cmd /k "cd backend && set ENVIRONMENT=production && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
start cmd /k "cd frontend && npm run dev"

echo Successfully started production processes!
pause
