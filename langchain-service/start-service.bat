@echo off
REM LangChain Service Startup Script for Windows

echo ================================================
echo  LangChain Workflow Service Startup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

echo [1/5] Python version check...
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo.
    echo [2/5] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo.
echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and set your OPENAI_API_KEY
    echo Press any key to open .env file in notepad...
    pause
    notepad .env
)

REM Check if OPENAI_API_KEY is set
for /f "tokens=2 delims==" %%a in ('findstr /i "OPENAI_API_KEY" .env') do set OPENAI_KEY=%%a
if "%OPENAI_KEY%"=="your-openai-api-key-here" (
    echo.
    echo ERROR: OPENAI_API_KEY not configured in .env file
    echo Please set your OpenAI API key in .env
    pause
    exit /b 1
)

echo.
echo [5/5] Starting LangChain Service...
echo.
echo ================================================
echo  Service Configuration:
echo ================================================
echo  Port: 8004
echo  API Docs: http://localhost:8004/docs
echo  Health: http://localhost:8004/health
echo ================================================
echo.
echo Press Ctrl+C to stop the service
echo.

REM Start the service
python main.py

pause
