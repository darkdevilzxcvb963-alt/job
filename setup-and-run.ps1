# Complete Setup and Run Script
# This script installs all dependencies and starts the project automatically

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI-Powered Resume Matching Platform" -ForegroundColor Cyan
Write-Host "Complete Setup and Run Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check PostgreSQL (optional check)
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL found: $pgVersion" -ForegroundColor Green
    } else {
        Write-Host "⚠ PostgreSQL not found in PATH (may still be installed)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ PostgreSQL not found in PATH (may still be installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Backend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install backend dependencies
Write-Host "Installing backend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

# Download SpaCy model
Write-Host "Downloading SpaCy model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm --quiet
Write-Host "✓ SpaCy model downloaded" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    
    # Check if .env.example exists
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "✓ Created .env from .env.example" -ForegroundColor Green
    } else {
        # Create basic .env file
        @"
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/resume_matching_db

# Security
SECRET_KEY=dev-secret-key-change-in-production-$(Get-Random)

# OpenAI API (Optional - for LLM features)
OPENAI_API_KEY=

# Email Configuration (Optional - for email verification)
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@resumematching.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=True
"@ | Out-File -FilePath .env -Encoding utf8
        Write-Host "✓ Created .env file with default values" -ForegroundColor Green
    }
    Write-Host "⚠ Please edit backend/.env file to configure your settings" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Check if database exists and run migrations
Write-Host "Checking database connection..." -ForegroundColor Yellow
Write-Host "Running database migrations..." -ForegroundColor Yellow
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database migrations completed" -ForegroundColor Green
} else {
    Write-Host "⚠ Database migration failed. Make sure PostgreSQL is running and DATABASE_URL is correct in .env" -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 2: Frontend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

# Install frontend dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Frontend dependencies already installed" -ForegroundColor Green
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 3: Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
$dockerAvailable = $false
try {
    $null = docker --version 2>&1
    $dockerAvailable = $true
} catch {
    $dockerAvailable = $false
}

if ($dockerAvailable) {
    Write-Host "Docker detected. Starting services with Docker..." -ForegroundColor Yellow
    Write-Host ""
    
    # Start Docker services
    docker-compose up -d
    
    Write-Host ""
    Write-Host "Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Run migrations in Docker
    Write-Host "Running database migrations in Docker..." -ForegroundColor Yellow
    docker-compose exec -T backend alembic upgrade head
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ All services started with Docker!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "Docker not available. Starting services manually..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Starting backend and frontend in separate windows..." -ForegroundColor Yellow
    
    # Start backend in new window
    Write-Host "Opening backend server..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; Write-Host 'Starting Backend Server...' -ForegroundColor Green; uvicorn app.main:app --reload"
    
    # Wait a bit for backend to start
    Start-Sleep -Seconds 3
    
    # Start frontend in new window
    Write-Host "Opening frontend server..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Starting Frontend Server...' -ForegroundColor Green; npm run dev"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Services starting in separate windows!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Application URLs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open http://localhost:3000 in your browser" -ForegroundColor Yellow
Write-Host "2. Sign up for a new account" -ForegroundColor Yellow
Write-Host "3. Verify your email (if email is configured)" -ForegroundColor Yellow
Write-Host "4. Start using the platform!" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Gray
if ($dockerAvailable) {
    Write-Host "  docker-compose down" -ForegroundColor Gray
} else {
    Write-Host "  Close the PowerShell windows" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
