@echo off
setlocal enabledelayedexpansion

:: Project Startup Script
echo ==========================================
echo   RESUME MATCHING PLATFORM - STARTUP
echo ==========================================
echo.

:: Define paths
set "BASE_DIR=%~dp0"
set "BACKEND_DIR=%BASE_DIR%backend"
set "FRONTEND_DIR=%BASE_DIR%frontend"
set "VENV_PYTHON=%BACKEND_DIR%\venv\Scripts\python.exe"

:: Check dependencies
if not exist "!VENV_PYTHON!" (
    echo [ERROR] Virtual environment not found at %VENV_PYTHON%
    echo Please ensure the backend is set up correctly.
    pause
    exit /b 1
)

:: Kill existing processes on ports 8000, 3000, 3001
echo [1/5] Cleaning up existing services and cache...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 "') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3001 "') do taskkill /PID %%a /F 2>nul

:: Clear Vite cache to ensure latest version is served
if exist "!FRONTEND_DIR!\node_modules\.vite" (
    echo [ACTION] Clearing Vite cache...
    rd /s /q "!FRONTEND_DIR!\node_modules\.vite"
)
timeout /t 1 /nobreak >nul

:: Database Initialization Option
echo.
echo [2/5] Database Initialization
set "choice="
set /p choice="Do you want to reset and seed the database with test data? (y/n) [Default: n]: "
if /i "!choice!"=="y" goto :init_db
echo [SKIP] Skipping database initialization.
goto :start_backend

:init_db
echo [ACTION] Initializing database...
cd /d "!BACKEND_DIR!"
"!VENV_PYTHON!" init_db_simple.py
echo [ACTION] Creating test data (Jobs, Candidates, Matches)...
"!VENV_PYTHON!" create_test_data.py
echo [SUCCESS] Database ready!

:start_backend

:: Start Backend
echo.
echo [3/5] Starting Backend Server (API, AI Engine on Port 8000)...
start "Backend Server" /min cmd /k "cd /d "!BACKEND_DIR!" && "!VENV_PYTHON!" run_server.py"

:: Wait for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Frontend
echo.
echo [4/5] Starting Frontend Server (UI on Port 3000)...
start "Frontend Server" /min cmd /k "cd /d "!FRONTEND_DIR!" && npm run dev"

:: Open Browser
echo.
echo [5/5] Opening application in browser...
timeout /t 8 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo ===========================================
echo   EVERYTHING IS RUNNING!
echo ===========================================
echo [UI]      http://localhost:3000
echo [API]     http://127.0.0.1:8000/docs
echo [MATCHES] Auto-calculated on login
echo [ADMIN]   View users at http://localhost:3000/admin
echo ===========================================
echo.
echo Keep the minimized windows open to keep the services running.
echo.
pause
