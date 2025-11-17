@echo off
echo ========================================
echo Service Health Check
echo ========================================
echo.

echo Checking Auth Service (8001)...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Auth Service is running
    curl http://localhost:8001/health
) else (
    echo ❌ Auth Service is NOT running
)
echo.

echo Checking Chat Service (8000)...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Chat Service is running
    curl http://localhost:8000/health
) else (
    echo ❌ Chat Service is NOT running
)
echo.

echo Checking Analytics Service (8002)...
curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Analytics Service is running
    curl http://localhost:8002/health
) else (
    echo ❌ Analytics Service is NOT running
)
echo.

echo Checking Frontend (3000)...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running
) else (
    echo ❌ Frontend is NOT running
)
echo.

echo ========================================
echo Health Check Complete
echo ========================================
echo.
echo If any service shows as NOT running:
echo 1. Check the terminal window for that service
echo 2. Look for error messages
echo 3. Try restarting that specific service
echo.
pause
