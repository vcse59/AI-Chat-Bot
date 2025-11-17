@echo off
echo Running manual requirements test...
cd /d "%~dp0"
python manual_requirements_test.py
echo.
echo Test completed!
echo Press any key to exit...
pause > nul
