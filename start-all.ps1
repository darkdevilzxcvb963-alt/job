# Start All Services Script
Write-Host "Starting All Services..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
try {
    docker --version | Out-Null
    $dockerAvailable = $true
} catch {
    $dockerAvailable = $false
}

if ($dockerAvailable) {
    Write-Host "Using Docker Compose..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check if .env exists
    if (-not (Test-Path "backend\.env")) {
        Write-Host "Creating backend/.env file..." -ForegroundColor Yellow
        Copy-Item backend\.env.example backend\.env
    }
    
    # Start services
    Write-Host "Starting services with Docker Compose..." -ForegroundColor Green
    docker-compose up -d
    
    Write-Host ""
    Write-Host "Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Initialize database
    Write-Host "Initializing database..." -ForegroundColor Yellow
    docker-compose exec -T backend alembic upgrade head
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "All services started!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the application:" -ForegroundColor Yellow
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "View logs: docker-compose logs -f" -ForegroundColor Gray
    Write-Host "Stop services: docker-compose down" -ForegroundColor Gray
} else {
    Write-Host "Docker not available. Starting services manually..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please run in separate terminals:" -ForegroundColor Yellow
    Write-Host "  1. .\start-backend.ps1" -ForegroundColor White
    Write-Host "  2. .\start-frontend.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or install Docker Desktop for easier management." -ForegroundColor Yellow
}
