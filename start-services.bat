@echo off
REM Master startup script - Launches both backend and frontend in separate processes
REM This allows both to run indefinitely without 60-second timeout

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo  Resume Matching Platform - Complete Startup
echo ============================================================================
echo.

REM Get the project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM Kill any existing processes
echo Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend Server in new window
echo.
echo Starting Backend Server (FastAPI on port 8000)...
echo ============================================================================
start "Resume Matching - Backend Server" cmd /k "cd /d "%PROJECT_ROOT%backend" && call venv\Scripts\activate && python run_server.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend Server in new window
echo.
echo Starting Frontend Server (Vite on port 3000)...
echo ============================================================================
start "Resume Matching - Frontend Server" cmd /k "cd /d "%PROJECT_ROOT%frontend" && npm run dev"

echo.
echo ============================================================================
echo Services Starting Up:
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://127.0.0.1:8000/docs
echo.
echo Both services are running in separate windows and will continue indefinitely.
echo Close either window to stop that service.
echo ============================================================================
echo.
timeout /t 8 /nobreak >nul
echo Opening browser to frontend...
start "" "http://localhost:3000"

endlocal
