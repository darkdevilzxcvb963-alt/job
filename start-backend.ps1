# Start Backend Server Script
Write-Host "Starting Backend Server..." -ForegroundColor Cyan

Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Running setup first..." -ForegroundColor Yellow
    Set-Location ..
    .\setup.ps1
    Set-Location backend
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠ Please edit .env file to add your OpenAI API key" -ForegroundColor Yellow
}

# Start the server
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs available at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
uvicorn app.main:app --reload
