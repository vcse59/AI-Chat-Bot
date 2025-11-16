@echo off
echo ============================================
echo   Check and Fix Admin Role
echo ============================================
echo.

echo Enter your username:
set /p username=

echo.
echo Checking user roles...
docker exec auth-server python3 -c "import sqlite3; conn = sqlite3.connect('/app/data/app.db'); cursor = conn.cursor(); cursor.execute('SELECT u.username, GROUP_CONCAT(r.name) as roles FROM users u LEFT JOIN user_roles ur ON u.id = ur.user_id LEFT JOIN roles r ON ur.role_id = r.id WHERE u.username=? GROUP BY u.username', ('%username%',)); result = cursor.fetchone(); print(f'User: {result[0]}, Roles: {result[1]}' if result else 'User not found'); conn.close()"

echo.
echo.
echo Do you want to add admin role to this user? (Y/N)
set /p confirm=

if /i "%confirm%"=="Y" (
    echo.
    echo Adding admin role...
    docker exec auth-server python3 -c "import sqlite3; conn = sqlite3.connect('/app/data/app.db'); cursor = conn.cursor(); cursor.execute('INSERT OR IGNORE INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username=? AND r.name=\"admin\"', ('%username%',)); conn.commit(); print(f'Rows affected: {cursor.rowcount}'); conn.close()"
    
    echo.
    echo Verifying...
    docker exec auth-server python3 -c "import sqlite3; conn = sqlite3.connect('/app/data/app.db'); cursor = conn.cursor(); cursor.execute('SELECT u.username, GROUP_CONCAT(r.name) as roles FROM users u LEFT JOIN user_roles ur ON u.id = ur.user_id LEFT JOIN roles r ON ur.role_id = r.id WHERE u.username=? GROUP BY u.username', ('%username%',)); result = cursor.fetchone(); print(f'User: {result[0]}, Roles: {result[1]}'); conn.close()"
    
    echo.
    echo ============================================
    echo   Admin role added successfully!
    echo ============================================
    echo.
    echo IMPORTANT: You must logout and login again!
    echo 1. Logout from the app
    echo 2. Login again with your credentials
    echo 3. You should now see the Analytics button
    echo.
) else (
    echo.
    echo Operation cancelled.
)

pause
