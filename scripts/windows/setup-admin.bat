@echo off
REM Setup Admin User Script
REM Creates an admin user with admin role

echo ============================================
echo Admin User Setup
echo ============================================
echo.

REM Check if auth-service venv exists
if not exist "%~dp0..\..\auth-service\venv\Scripts\python.exe" (
    echo ERROR: Auth service virtual environment not found!
    echo Please run setup-venv.bat first
    echo.
    pause
    exit /b 1
)

REM Run the setup script using auth-service venv
"%~dp0..\..\auth-service\venv\Scripts\python.exe" "%~dp0setup-admin.py" %*

echo.
pause
