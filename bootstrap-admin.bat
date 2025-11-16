@echo off
REM Bootstrap First Admin User - Windows Script
REM This script creates your first admin user

echo ============================================
echo   Bootstrap First Admin User
echo ============================================
echo.

REM Step 1: Create regular user via API
echo Step 1: Creating user via API...
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
echo Creating user: %username%
curl -X POST http://localhost:8001/auth/register -H "Content-Type: application/json" -d "{\"username\":\"%username%\",\"email\":\"%email%\",\"password\":\"%password%\",\"full_name\":\"%username%\"}"

echo.
echo.
echo Step 2: Adding admin role to database...
echo.

REM Step 2: Update database
docker exec -it auth-server sqlite3 /app/data/auth.db "INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username='%username%' AND r.name='admin';"

echo.
echo Step 3: Verifying admin role...
docker exec -it auth-server sqlite3 /app/data/auth.db "SELECT u.username, r.name FROM users u JOIN user_roles ur ON u.id = ur.user_id JOIN roles r ON ur.role_id = r.id WHERE u.username='%username%';"

echo.
echo ============================================
echo   Bootstrap Complete!
echo ============================================
echo.
echo Username: %username%
echo Password: %password%
echo.
echo Next steps:
echo 1. Go to http://localhost:3000/login
echo 2. Login with the credentials above
echo 3. You should see Analytics and Create Admin buttons
echo.
pause
