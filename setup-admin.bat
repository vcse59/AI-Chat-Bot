@echo off
echo ============================================
echo   Complete Admin Setup
echo ============================================
echo.
echo This will create your first admin account.
echo.

:input
echo Enter username (default: admin):
set /p username=
if "%username%"=="" set username=admin

echo Enter email (default: admin@example.com):
set /p email=
if "%email%"=="" set email=admin@example.com

echo Enter password (default: admin123):
set /p password=
if "%password%"=="" set password=admin123

echo.
echo Creating admin account...
echo Username: %username%
echo Email: %email%
echo.

REM Register user
echo Step 1: Registering user via API...
curl -X POST http://localhost:8001/auth/register -H "Content-Type: application/json" -d "{\"username\":\"%username%\",\"email\":\"%email%\",\"password\":\"%password%\",\"full_name\":\"%username%\"}"

echo.
echo.
echo Step 2: Adding admin role...

REM Copy script to container
docker cp check_roles.py auth-server:/tmp/check_roles.py

REM Add admin role
docker exec auth-server python /tmp/check_roles.py %username% add

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Credentials:
echo   Username: %username%
echo   Password: %password%
echo.
echo Next steps:
echo   1. Go to http://localhost:3000/login
echo   2. Login with the credentials above
echo   3. You should see "Analytics" and "Create Admin" buttons
echo.
echo IMPORTANT: If already logged in, you must LOGOUT and LOGIN again!
echo.
pause
