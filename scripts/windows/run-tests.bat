@echo off
echo ========================================
echo Running Tests
echo ========================================
echo.

cd /d "%~dp0..\..\tests"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run setup-venv.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

echo Running manual requirements test...
echo.

python manual_requirements_test.py

echo.
echo ========================================
echo Tests completed!
echo ========================================
echo.
pause
