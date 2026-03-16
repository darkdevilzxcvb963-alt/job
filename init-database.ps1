# Initialize Database Script
Write-Host "Initializing Database..." -ForegroundColor Cyan

Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if database is accessible
Write-Host "Checking database connection..." -ForegroundColor Yellow
$env:PYTHONPATH = "."
python -c "from app.core.database import engine; engine.connect(); print('✓ Database connection successful')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Database connection failed. Please ensure PostgreSQL is running." -ForegroundColor Yellow
    Write-Host "You can start PostgreSQL with Docker: docker-compose up -d db" -ForegroundColor Yellow
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database initialized successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Database initialization failed. Please check the error above." -ForegroundColor Red
}

Set-Location ..
