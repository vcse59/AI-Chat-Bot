@echo off
echo.
echo ================================================================================
echo  AI Chat Bot - Requirements Verification
echo ================================================================================
echo.

cd /d "%~dp0"
python manual_requirements_test.py

pause
