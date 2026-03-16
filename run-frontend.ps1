# Frontend Launcher Script
Write-Host "Starting Resume Matching Frontend..." -ForegroundColor Cyan
Write-Host "This session will run indefinitely until manually stopped." -ForegroundColor Yellow

# Navigate to frontend directory
$frontendPath = "$PSScriptRoot\frontend"
Set-Location $frontendPath

# Install dependencies if needed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
npm install --silent | Out-Null

# Start dev server with extended runtime
Write-Host "Starting Vite dev server on http://localhost:3000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Set environment variables for extended runtime
$env:NODE_ENV = "development"
$env:VITE_REQUEST_TIMEOUT = "300000"

npm run dev -- --clearScreen=false

# Keep the terminal open after process ends
Read-Host "Press Enter to exit"
