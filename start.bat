@echo off
REM Quick Start Script for Open ChatBot Platform (Windows)

echo.
echo 🚀 Starting Open ChatBot Platform...
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo ✅ Created .env file. Please update it with your API keys:
    echo    - AUTH_SECRET_KEY (required^)
    echo    - OPENAI_API_KEY (required^)
    echo.
    pause
)

echo 🐳 Starting Docker Compose...
docker-compose up --build

echo.
echo ✨ Services starting...
echo    - React Frontend:  http://localhost:3000
echo    - Auth Server:     http://localhost:8001
echo    - ChatBot Service: http://localhost:8000
echo.
echo 📚 API Documentation:
echo    - Auth API:  http://localhost:8001/docs
echo    - Chat API:  http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop all services
pause
