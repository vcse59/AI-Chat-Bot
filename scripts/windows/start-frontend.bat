@echo off
echo ========================================
echo Starting React Frontend on Port 3000
echo ========================================
echo.

cd /d "%~dp0..\..\chat-frontend"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo ❌ Node modules not found!
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting React Frontend...
echo URL: http://localhost:3000
echo.

REM Set environment variables for backend URLs
set REACT_APP_AUTH_API_URL=http://localhost:8001
set REACT_APP_CHAT_API_URL=http://localhost:8000
set REACT_APP_ANALYTICS_API_URL=http://localhost:8002

REM Run the frontend
call npm start

pause
