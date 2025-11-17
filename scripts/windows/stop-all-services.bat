@echo off
echo ========================================
echo Stopping All Services
echo ========================================
echo.

echo Killing Python processes (Auth, Chat, Analytics)...
taskkill /F /FI "WINDOWTITLE eq Auth Service*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Chat Service*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Analytics Service*" 2>nul

echo Killing Node processes (Frontend)...
taskkill /F /FI "WINDOWTITLE eq Frontend*" 2>nul

echo.
echo ✅ All services stopped!
echo.
pause
