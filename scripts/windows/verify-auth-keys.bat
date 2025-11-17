@echo off
echo ============================================
echo Verifying AUTH_SECRET_KEY Configuration
echo ============================================
echo.

echo Root .env file:
findstr "AUTH_SECRET_KEY" .env
echo.

echo Auth Service:
echo   - Looking for AUTH_SECRET_KEY in code...
findstr /C:"AUTH_SECRET_KEY" auth-service\auth_server\security\auth.py
echo.

echo Chat Service:
echo   - Looking for AUTH_SECRET_KEY in code...
findstr /C:"AUTH_SECRET_KEY" chat-service\security\oauth.py
echo.

echo Analytics Service:
echo   - Looking for AUTH_SECRET_KEY in code...
findstr /C:"AUTH_SECRET_KEY" analytics-service\analytics\security\auth.py
echo.

echo ============================================
echo If all services show "AUTH_SECRET_KEY", configuration is correct!
echo If any service shows "SECRET_KEY", that service needs to be updated.
echo ============================================
pause

