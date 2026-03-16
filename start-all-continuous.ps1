# Start All Services - Continuous Version
# This script will keep both backend and frontend running continuously
# even if they crash

Write-Host "Starting All Services (Continuous Mode)..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend/.env file..." -ForegroundColor Yellow
    if (Test-Path "backend\.env.example") {
        Copy-Item backend\.env.example backend\.env
        Write-Host ".env file created" -ForegroundColor Green
    } else {
        Write-Host "WARNING: No .env.example found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting Services..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Opening two new PowerShell windows:" -ForegroundColor Cyan
Write-Host "1. Backend (Port 8000) - http://localhost:8000" -ForegroundColor White
Write-Host "2. Frontend (Port 3000) - http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in any window to stop a service" -ForegroundColor Yellow
Write-Host "Services will auto-restart if they crash" -ForegroundColor Yellow
Write-Host ""

# Start backend in a new window
Write-Host "Starting Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; & '$PWD\run-backend-continuous.ps1'"
Start-Sleep -Seconds 2

# Start frontend in a new window
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; & '$PWD\..\run-frontend-continuous.ps1'"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services Starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Admin Credentials:" -ForegroundColor Yellow
Write-Host "  Email: admin@example.com" -ForegroundColor White
Write-Host "  Password: Admin@1234" -ForegroundColor White
Write-Host ""
Write-Host "Note: This window can be closed. Services run in separate windows." -ForegroundColor Cyan
