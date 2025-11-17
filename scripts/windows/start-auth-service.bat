@echo off
echo ========================================
echo Starting Auth Service on Port 8001
echo ========================================
echo.

cd /d "%~dp0..\..\auth-service"

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
if not defined PORT set PORT=8001
if not defined HOST set HOST=0.0.0.0

echo Starting Auth Service...
echo URL: http://localhost:8001
echo Docs: http://localhost:8001/docs
echo.

REM Run the service
python -m uvicorn auth_server.main:app --host 0.0.0.0 --port 8001 --reload

pause
