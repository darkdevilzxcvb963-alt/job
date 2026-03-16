@echo off
REM Quick Status Checker - Verifies both services are running

echo.
echo ============================================================================
echo  Resume Matching Platform - Status Check
echo ============================================================================
echo.

setlocal enabledelayedexpansion

REM Check Backend
echo Checking Backend (http://127.0.0.1:8000)...
for /f "tokens=*" %%i in ('powershell -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/docs' -UseBasicParsing -TimeoutSec 5).StatusCode } catch { Write-Host 'ERROR' }"') do set "BACKEND_STATUS=%%i"

if "!BACKEND_STATUS!"=="200" (
    echo [OK] Backend is running ✓
) else (
    echo [ERROR] Backend is NOT running ✗
)

REM Check Frontend
echo Checking Frontend (http://localhost:3000)...
for /f "tokens=*" %%i in ('powershell -Command "try { (Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 5).StatusCode } catch { Write-Host 'ERROR' }"') do set "FRONTEND_STATUS=%%i"

if "!FRONTEND_STATUS!"=="200" (
    echo [OK] Frontend is running ✓
) else (
    echo [ERROR] Frontend is NOT running ✗
)

echo.
echo ============================================================================
echo  Summary
echo ============================================================================

if "!BACKEND_STATUS!"=="200" if "!FRONTEND_STATUS!"=="200" (
    echo All services are running correctly!
    echo.
    echo Backend:  http://127.0.0.1:8000/docs
    echo Frontend: http://localhost:3000
    echo.
    echo Status: READY TO USE ✓
) else (
    echo One or more services are not running.
    echo.
    if NOT "!BACKEND_STATUS!"=="200" (
        echo Backend is not running. Start with:
        echo   cd backend
        echo   python run_server.py
    )
    if NOT "!FRONTEND_STATUS!"=="200" (
        echo Frontend is not running. Start with:
        echo   cd frontend
        echo   npm run dev
    )
)

echo ============================================================================
echo.

endlocal
