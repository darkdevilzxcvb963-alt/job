# Backend Launcher Script
Write-Host "Starting Resume Matching Backend..." -ForegroundColor Cyan

# Navigate to backend directory
$backendPath = "$PSScriptRoot\backend"
Set-Location $backendPath

# Activate virtual environment
& "$backendPath\venv\Scripts\Activate.ps1"

# Start uvicorn
Write-Host "Starting Uvicorn server on http://0.0.0.0:8000..." -ForegroundColor Green
Write-Host "API Docs available at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
