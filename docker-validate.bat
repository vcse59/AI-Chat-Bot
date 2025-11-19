@echo off
REM Docker Deployment and Validation Script for ConvoAI with MCP Integration
REM This script builds, starts, and validates all services in Docker

setlocal enabledelayedexpansion

echo ========================================
echo ConvoAI Docker Deployment with MCP
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env file and set:
    echo   1. OPENAI_API_KEY=your-actual-api-key
    echo   2. AUTH_SECRET_KEY=your-secure-secret-key
    echo.
    echo Press any key to continue after updating .env file...
    pause >nul
)

REM Verify OpenAI API key is set
findstr /C:"OPENAI_API_KEY=sk-" .env >nul 2>&1
if errorlevel 1 (
    echo [ERROR] OPENAI_API_KEY not properly set in .env file
    echo Please edit .env and set: OPENAI_API_KEY=sk-your-key
    exit /b 1
)

echo [OK] Environment configuration found
echo.

REM Stop any running containers
echo Step 1: Stopping existing containers...
docker-compose down
echo.

REM Build all services
echo Step 2: Building Docker images...
echo This may take a few minutes on first run...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Docker build failed
    exit /b 1
)
echo [OK] All images built successfully
echo.

REM Start services
echo Step 3: Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)
echo [OK] All services started
echo.

REM Wait for services to be ready
echo Step 4: Waiting for services to be healthy...
echo This may take 30-60 seconds...

set MAX_WAIT=60
set WAIT_COUNT=0

:wait_loop
if %WAIT_COUNT% geq %MAX_WAIT% (
    echo [ERROR] Services did not become healthy in time
    echo.
    echo Checking service logs:
    docker-compose logs --tail=50
    exit /b 1
)

REM Check auth-server health
curl -s http://localhost:8001/health >nul 2>&1
set AUTH_STATUS=!errorlevel!

REM Check chat-service health
curl -s http://localhost:8000/health >nul 2>&1
set CHAT_STATUS=!errorlevel!

REM Check timezone-mcp-server health
curl -s http://localhost:8003/health >nul 2>&1
set MCP_STATUS=!errorlevel!

if !AUTH_STATUS! equ 0 if !CHAT_STATUS! equ 0 if !MCP_STATUS! equ 0 (
    goto services_ready
)

timeout /t 2 /nobreak >nul
set /a WAIT_COUNT+=2
goto wait_loop

:services_ready
echo [OK] All services are healthy!
echo.

REM Display service status
echo ========================================
echo Service Status
echo ========================================
echo.
echo [✓] Auth Service:     http://localhost:8001
echo [✓] Chat Service:     http://localhost:8000
echo [✓] MCP Server:       http://localhost:8003
echo [✓] Frontend:         http://localhost:3000
echo [✓] Nginx (prod):     http://localhost:80
echo.

REM Show running containers
echo Running Containers:
docker-compose ps
echo.

REM Validate MCP integration
echo ========================================
echo Validating MCP Integration
echo ========================================
echo.

echo Test 1: Check MCP server tools endpoint...
curl -s http://localhost:8003/tools | findstr "tools" >nul 2>&1
if errorlevel 1 (
    echo [FAIL] MCP server tools endpoint not responding
) else (
    echo [PASS] MCP server exposes tools endpoint
)
echo.

echo Test 2: Create test user and authenticate...
set TIMESTAMP=%time::=%
set TIMESTAMP=%TIMESTAMP: =0%
set TEST_USER=dockertest_%TIMESTAMP%

REM Register user
curl -s -X POST http://localhost:8001/users/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"%TEST_USER%\",\"email\":\"%TEST_USER%@test.com\",\"password\":\"Test123!\"}" ^
  > temp_register.json 2>&1

findstr "id" temp_register.json >nul 2>&1
if errorlevel 1 (
    echo [FAIL] User registration failed
    type temp_register.json
    del temp_register.json
    goto cleanup
)
echo [PASS] User registered successfully
echo.

REM Login to get token
curl -s -X POST http://localhost:8001/auth/token ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=%TEST_USER%&password=Test123!" ^
  > temp_token.json 2>&1

REM Extract access token (basic parsing)
for /f "tokens=2 delims=:," %%a in ('findstr "access_token" temp_token.json') do (
    set TOKEN_RAW=%%a
)
set TOKEN=%TOKEN_RAW:"=%
set TOKEN=%TOKEN: =%

if "%TOKEN%"=="" (
    echo [FAIL] Failed to get access token
    type temp_token.json
    del temp_token.json temp_register.json
    goto cleanup
)
echo [PASS] User authenticated successfully
echo.

echo Test 3: Register MCP server...
curl -s -X POST http://localhost:8000/mcp-servers/ ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Timezone MCP\",\"description\":\"Test MCP server\",\"server_url\":\"http://timezone-mcp-server:8003\",\"api_key\":\"%TOKEN%\",\"is_active\":true}" ^
  > temp_mcp.json 2>&1

findstr "id" temp_mcp.json >nul 2>&1
if errorlevel 1 (
    echo [FAIL] MCP server registration failed
    type temp_mcp.json
    del temp_*.json
    goto cleanup
)
echo [PASS] MCP server registered successfully
echo.

echo Test 4: Create conversation...
curl -s -X POST http://localhost:8000/conversations/ ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Docker Test\",\"system_message\":\"You are a helpful assistant.\"}" ^
  > temp_conv.json 2>&1

for /f "tokens=2 delims=:," %%a in ('findstr "\"id\"" temp_conv.json') do (
    set CONV_RAW=%%a
)
set CONV_ID=%CONV_RAW:"=%
set CONV_ID=%CONV_ID: =%

if "%CONV_ID%"=="" (
    echo [FAIL] Failed to create conversation
    type temp_conv.json
    del temp_*.json
    goto cleanup
)
echo [PASS] Conversation created: %CONV_ID%
echo.

echo Test 5: Send message with MCP tool requirement...
echo Sending: "What time is it in Tokyo?"
echo This will test the complete MCP integration flow...
curl -s -X POST http://localhost:8000/messages/ ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"conversation_id\":\"%CONV_ID%\",\"content\":\"What time is it in Tokyo?\"}" ^
  > temp_message.json 2>&1

findstr "ai_response" temp_message.json >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Message processing failed
    type temp_message.json
) else (
    echo [PASS] Message processed successfully
    echo.
    echo Response preview:
    findstr "content" temp_message.json | findstr /v "conversation_id"
)
echo.

REM Cleanup temp files
del temp_*.json 2>nul

:cleanup
echo ========================================
echo Validation Complete
echo ========================================
echo.

echo Next Steps:
echo.
echo 1. View logs:           docker-compose logs -f
echo 2. View specific logs:  docker-compose logs -f openai-chatbot
echo 3. Run full tests:      cd tests ^&^& pytest test_8_mcp_integration.py -v -s
echo 4. Stop services:       docker-compose down
echo 5. Access frontend:     http://localhost:3000
echo.
echo For detailed testing, run:
echo   cd tests
echo   pytest test_8_mcp_integration.py -v -s
echo.

pause
