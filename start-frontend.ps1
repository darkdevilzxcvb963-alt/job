# Start Frontend Server Script
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
Write-Host "This session will run indefinitely until manually stopped." -ForegroundColor Yellow

Set-Location frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Dependencies not found. Installing..." -ForegroundColor Yellow
    npm install
}

# Set environment variables for extended runtime
$env:NODE_ENV = "development"
$env:VITE_REQUEST_TIMEOUT = "300000"

# Start the development server with extended settings
Write-Host "Starting React development server on http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

npm run dev -- --clearScreen=false

# Keep the terminal open after process ends
Read-Host "Press Enter to exit"
