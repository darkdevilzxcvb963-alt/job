@echo off
echo ========================================================
echo 🐳 DOCKER PRODUCTION DEPLOYMENT TEST
echo ========================================================
echo.
echo This script will use Docker Compose to spin up your entire
echo projected production environment on your laptop (Port 80).
echo.
echo Ensure Docker Desktop is open and running!
echo.

docker-compose -f docker-compose.prod.yml up --build -d

echo.
echo If successful, your production App is running!
echo Open your browser to: http://localhost
echo.
echo To stop the deployment run:
echo docker-compose -f docker-compose.prod.yml down
echo.
pause
