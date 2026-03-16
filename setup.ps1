# AI-Powered Resume & Job Matching Platform - Setup Script
# This script automates the setup process for Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI-Powered Resume & Job Matching Platform" -ForegroundColor Cyan
Write-Host "Automated Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if Docker is installed (optional)
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
    $dockerAvailable = $true
} catch {
    Write-Host "⚠ Docker not found. You can still run manually." -ForegroundColor Yellow
    $dockerAvailable = $false
}

Write-Host ""
Write-Host "Setting up backend..." -ForegroundColor Cyan

# Navigate to backend directory
Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install Python dependencies
Write-Host "Installing Python dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt

# Download SpaCy model
Write-Host "Downloading SpaCy model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created. Please edit it to add your OpenAI API key." -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create uploads directory
if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" | Out-Null
    Write-Host "✓ Uploads directory created" -ForegroundColor Green
}

Set-Location ..

Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location frontend

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies (this may take a few minutes)..." -ForegroundColor Yellow
npm install

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend/.env and add your OpenAI API key (optional)" -ForegroundColor White
Write-Host "2. Set up PostgreSQL database:" -ForegroundColor White
Write-Host "   - Install PostgreSQL if not installed" -ForegroundColor White
Write-Host "   - Create database: createdb resume_matching_db" -ForegroundColor White
Write-Host "   - Or use Docker: docker-compose up -d db" -ForegroundColor White
Write-Host "3. Run database migrations:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   alembic upgrade head" -ForegroundColor White
Write-Host "4. Start the backend server:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "5. Start the frontend server (in a new terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Or use Docker Compose:" -ForegroundColor Yellow
if ($dockerAvailable) {
    Write-Host "   docker-compose up -d" -ForegroundColor White
} else {
    Write-Host "   (Docker not available - install Docker Desktop first)" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
