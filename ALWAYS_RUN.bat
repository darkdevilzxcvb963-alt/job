@echo off
setlocal enabledelayedexpansion

:: ALWAYS RUN SCRIPT
:: Starts Backend and Frontend immediately without prompts.

echo ==========================================
echo   RESUME MATCHING PLATFORM - AUTO START
echo ==========================================
echo.

set "BASE_DIR=%~dp0"
set "BACKEND_DIR=%BASE_DIR%backend"
set "FRONTEND_DIR=%BASE_DIR%frontend"
set "VENV_PYTHON=%BACKEND_DIR%\venv\Scripts\python.exe"

:: 1. Cleanup existing ports 8000 and 3000
echo [1/4] Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 "') do taskkill /PID %%a /F 2>nul
timeout /t 1 /nobreak >nul

:: 2. Start Backend
echo [2/4] Starting Backend...
if not exist "!VENV_PYTHON!" (
    echo [ERROR] Backend virtual environment not found!
    pause
    exit /b 1
)
start "Backend Server" /min cmd /k "cd /d "!BACKEND_DIR!" && "!VENV_PYTHON!" run_server.py"

:: 3. Start Frontend
echo [3/4] Starting Frontend...
start "Frontend Server" /min cmd /k "cd /d "!FRONTEND_DIR!" && npm run dev"

:: 4. Open Browser
echo [4/4] Opening Browser...
timeout /t 8 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo ===========================================
echo   SYSTEM IS RUNNING
echo ===========================================
echo   Use Google Sign-up now.
echo   Do not close the minimized windows.
echo ===========================================
pause
