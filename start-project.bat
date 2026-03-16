@echo off
REM Start Resume Matching Platform - Backend and Frontend continuously
REM This keeps both services running without time limits

setlocal enabledelayedexpansion

echo.
echo ================================
echo Resume Matching Platform Startup
echo ================================
echo.

REM Kill existing processes on ports 8000, 3000, 3001
echo Checking for existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 "') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3001 "') do taskkill /PID %%a /F 2>nul

timeout /t 1 /nobreak

echo.
echo Starting services...
echo.

REM Start Backend in new window (runs continuously)
echo [1/2] Starting Backend Server (Port 8000)...
start "Backend Server" /min cmd /k "cd /d C:\Users\ADMIN\new-project\backend && .\venv\Scripts\python.exe run_server.py"
timeout /t 3 /nobreak

REM Start Frontend in new window (runs continuously)
echo [2/2] Starting Frontend Server (Port 3000)...
start "Frontend Server" /min cmd /k "cd /d C:\Users\ADMIN\new-project\frontend && npm run dev"

echo.
echo ================================
echo Services Running Successfully!
echo ================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000 (or http://localhost:3001)
echo.
echo Test Credentials:
echo   Recruiter:  recruiter@example.com / Recruiter@1234
echo   Candidate:  jobseeker@example.com / Jobseeker@1234
echo.
echo Close these windows to stop the services.
echo.
pause
