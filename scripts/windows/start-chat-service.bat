@echo off
echo ========================================
echo Starting Chat Service on Port 8000
echo ========================================
echo.

@echo off
REM Navigate to chat service directory
REM Use %~dp0 to get script's directory, then navigate relative to project root

REM Get the project root (2 levels up from scripts/windows/)
cd /d "%~dp0..\..\chat-service"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run setup-venv.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Load environment variables from .env file
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1"=="#" set "%%a=%%b"
    )
)

REM Set environment variables
if not defined PORT set PORT=8000
if not defined HOST set HOST=0.0.0.0

echo Starting Chat Service...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo WebSocket: ws://localhost:8000/ws/chat
echo.

if not defined OPENAI_API_KEY (
    echo ⚠️  WARNING: OPENAI_API_KEY not set!
    echo Chat functionality may not work without it.
    echo Set it in chat-service/.env file.
    echo.
) else (
    echo ✅ OPENAI_API_KEY is configured
    echo.
)

REM Run the service
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause
