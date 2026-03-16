# Start Resume Matching Platform - Backend and Frontend
# This script keeps both services running continuously

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Resume Matching Platform Startup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check and kill any existing processes on ports 8000 and 3000/3001
Write-Host "Checking for existing services..." -ForegroundColor Yellow

$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "Killing existing process on port 8000..." -ForegroundColor Yellow
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "Killing existing process on port 3000..." -ForegroundColor Yellow
    Stop-Process -Id $port3000.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

$port3001 = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue
if ($port3001) {
    Write-Host "Killing existing process on port 3001..." -ForegroundColor Yellow
    Stop-Process -Id $port3001.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "[1/2] Starting Backend Server (Port 8000)..." -ForegroundColor Cyan
$backendProcess = Start-Process -NoNewWindow -PassThru -FilePath "cmd" -ArgumentList "/c cd `"C:\Users\ADMIN\new-project\backend`" && .\venv\Scripts\python.exe run_server.py"
$global:backendPID = $backendProcess.Id
Write-Host "✓ Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Green

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Frontend Server (Port 3000)..." -ForegroundColor Cyan
$frontendProcess = Start-Process -NoNewWindow -PassThru -FilePath "cmd" -ArgumentList "/c cd `"C:\Users\ADMIN\new-project\frontend`" && npm run dev"
$global:frontendPID = $frontendProcess.Id
Write-Host "✓ Frontend process started (PID: $($frontendProcess.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✓ Services Running Successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 Frontend: http://localhost:3000 (or http://localhost:3001)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  Recruiter:  recruiter@example.com / Recruiter@1234" -ForegroundColor White
Write-Host "  Candidate:  jobseeker@example.com / Jobseeker@1234" -ForegroundColor White
Write-Host ""
Write-Host "⏸️  Press CTRL+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Monitor processes and restart if they crash
$checkInterval = 10
while ($true) {
    Start-Sleep -Seconds $checkInterval
    
    # Check backend
    try {
        $backendProcessCheck = Get-Process -Id $global:backendPID -ErrorAction SilentlyContinue
        if (-not $backendProcessCheck) {
            Write-Host "⚠️  Backend crashed, restarting..." -ForegroundColor Yellow
            $backendProcess = Start-Process -NoNewWindow -PassThru -FilePath "cmd" -ArgumentList "/c cd `"C:\Users\ADMIN\new-project\backend`" && .\venv\Scripts\python.exe run_server.py"
            $global:backendPID = $backendProcess.Id
            Write-Host "✓ Backend restarted (PID: $($backendProcess.Id))" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Backend crashed, restarting..." -ForegroundColor Yellow
        $backendProcess = Start-Process -NoNewWindow -PassThru -FilePath "cmd" -ArgumentList "/c cd `"C:\Users\ADMIN\new-project\backend`" && .\venv\Scripts\python.exe run_server.py"
        $global:backendPID = $backendProcess.Id
        Write-Host "✓ Backend restarted (PID: $($backendProcess.Id))" -ForegroundColor Green
    }
    
    # Check frontend
    try {
        $frontendProcessCheck = Get-Process -Id $global:frontendPID -ErrorAction SilentlyContinue
        if (-not $frontendProcessCheck) {
            Write-Host "⚠️  Frontend crashed, restarting..." -ForegroundColor Yellow
            $frontendProcess = Start-Process -NoNewWindow -PassThru -FilePath "cmd" -ArgumentList "/c cd `"C:\Users\ADMIN\new-project\frontend`" && npm run dev"
            $global:frontendPID = $frontendProcess.Id
            Write-Host "✓ Frontend restarted (PID: $($frontendProcess.Id))" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Frontend crashed, restarting..." -ForegroundColor Yellow
        $frontendProcess = Start-Process -NoNewWindow -PassThru -FilePath "cmd" -ArgumentList "/c cd `"C:\Users\ADMIN\new-project\frontend`" && npm run dev"
        $global:frontendPID = $frontendProcess.Id
        Write-Host "✓ Frontend restarted (PID: $($frontendProcess.Id))" -ForegroundColor Green
    }
}
