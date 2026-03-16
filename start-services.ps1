# PowerShell script to start both backend and frontend services indefinitely
# This solves the 60-second timeout issue by running each in separate processes
# Frontend uses Python wrapper with auto-restart for extended uptime

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  Resume Matching Platform - Complete Startup" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Function to start backend
function Start-Backend {
    Write-Host ""
    Write-Host "Starting Backend Server (FastAPI on port 8000)..." -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    $backendPath = Join-Path $ProjectRoot "backend"
    $pythonExe = Join-Path $backendPath "venv\Scripts\python.exe"
    
    if (-not (Test-Path $pythonExe)) {
        Write-Host "ERROR: Python executable not found at $pythonExe" -ForegroundColor Red
        return $false
    }
    
    # Start backend in new PowerShell window with persistent runner
    $BackendScript = @"
`$projectRoot = '$ProjectRoot'
Set-Location (Join-Path `$projectRoot 'backend')
Write-Host "Backend starting in: " (Get-Location)
& "$pythonExe" run_server.py
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendScript -WindowStyle Normal
    Write-Host "✓ Backend process started" -ForegroundColor Green
    return $true
}

# Function to start frontend with auto-restart
function Start-Frontend {
    Write-Host ""
    Write-Host "Starting Frontend Server (Vite + Auto-Restart on port 3000)..." -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    $frontendPath = Join-Path $ProjectRoot "frontend"
    $pythonExe = Join-Path $ProjectRoot "backend\venv\Scripts\python.exe"
    
    if (-not (Test-Path $frontendPath)) {
        Write-Host "ERROR: Frontend directory not found at $frontendPath" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path (Join-Path $frontendPath "run_dev.py"))) {
        Write-Host "ERROR: Frontend runner (run_dev.py) not found" -ForegroundColor Red
        return $false
    }
    
    # Start frontend with Python wrapper for auto-restart on crash
    $FrontendScript = @"
`$projectRoot = '$ProjectRoot'
Set-Location (Join-Path `$projectRoot 'frontend')
Write-Host "Frontend starting in: " (Get-Location)
& "$pythonExe" run_dev.py
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendScript -WindowStyle Normal
    Write-Host "✓ Frontend process started (with auto-restart)" -ForegroundColor Green
    return $true
}

# Main execution
$backendOk = Start-Backend
Start-Sleep -Seconds 3

$frontendOk = Start-Frontend
Start-Sleep -Seconds 2

if ($backendOk -and $frontendOk) {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host "Services Starting Up:" -ForegroundColor Green
    Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Both services are running in separate windows and will continue indefinitely." -ForegroundColor Yellow
    Write-Host "Close any window to stop that service." -ForegroundColor Yellow
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host ""
    
    # Try to open browser
    Write-Host "Opening browser to frontend..." -ForegroundColor Cyan
    Start-Process "http://localhost:3000"
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to start services" -ForegroundColor Red
    exit 1
}
