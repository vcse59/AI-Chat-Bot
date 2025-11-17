@echo off
echo ========================================
echo Starting All Services
echo ========================================
echo.

echo This will open 4 terminal windows:
echo   1. Auth Service (Port 8001)
echo   2. Chat Service (Port 8000)
echo   3. Analytics Service (Port 8002)
echo   4. Frontend (Port 3000)
echo.
echo Press any key to continue...
pause > nul

REM Start Auth Service in new window
start "Auth Service (8001)" cmd /k "%~dp0start-auth-service.bat"
timeout /t 3 /nobreak > nul

REM Start Chat Service in new window
start "Chat Service (8000)" cmd /k "%~dp0start-chat-service.bat"
timeout /t 3 /nobreak > nul

REM Start Analytics Service in new window
start "Analytics Service (8002)" cmd /k "%~dp0start-analytics-service.bat"
timeout /t 3 /nobreak > nul

REM Start Frontend in new window
start "Frontend (3000)" cmd /k "%~dp0start-frontend.bat"

echo.
echo ========================================
echo All services starting...
echo ========================================
echo.
echo Services:
echo   Auth:      http://localhost:8001
echo   Chat:      http://localhost:8000
echo   Analytics: http://localhost:8002
echo   Frontend:  http://localhost:3000
echo.
echo Check each terminal window for status.
echo.
pause
