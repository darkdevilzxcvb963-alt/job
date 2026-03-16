# PowerShell script to run backend continuously
# Usage: .\run-backend-continuous.ps1

$venvPython = ".\venv\Scripts\python.exe"
$maxRetries = 10
$retryDelay = 3

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resume Matching Backend Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Make sure you run 'python -m venv venv' first" -ForegroundColor Yellow
    exit 1
}

$retryCount = 0

while ($true) {
    $retryCount++
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host "[$timestamp] Starting backend server..." -ForegroundColor Yellow
    Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    
    & $venvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
    
    $exitCode = $LASTEXITCODE
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host ""
    Write-Host "[$timestamp] Server stopped with exit code: $exitCode" -ForegroundColor Yellow
    
    if ($retryCount -lt $maxRetries) {
        Write-Host "Restarting in $retryDelay seconds... (Attempt $retryCount/$maxRetries)" -ForegroundColor Cyan
        Start-Sleep -Seconds $retryDelay
    } else {
        Write-Host "Max retries reached. Stopping." -ForegroundColor Red
        break
    }
}
