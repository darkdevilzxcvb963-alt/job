# PowerShell script to run frontend continuously
# Usage: .\run-frontend-continuous.ps1

$maxRetries = 10
$retryDelay = 3

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resume Matching Frontend Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$retryCount = 0

while ($true) {
    $retryCount++
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host "[$timestamp] Starting frontend dev server..." -ForegroundColor Yellow
    Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    
    & npm run dev
    
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
