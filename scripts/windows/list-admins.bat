@echo off
REM List Admin Users Script
REM Shows all users with admin role

REM Check if auth-service venv exists
if not exist "%~dp0..\..\auth-service\venv\Scripts\python.exe" (
    echo ERROR: Auth service virtual environment not found!
    echo Please run setup-venv.bat first
    echo.
    pause
    exit /b 1
)

REM Run the setup script with --list flag
"%~dp0..\..\auth-service\venv\Scripts\python.exe" "%~dp0setup-admin.py" --list

echo.
pause
