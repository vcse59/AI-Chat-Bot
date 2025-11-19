@echo off
REM Quick test runner for MCP Integration tests
REM Make sure all services are running before executing this script

echo ========================================
echo MCP Integration Test Runner
echo ========================================
echo.
echo Prerequisites:
echo - auth-service running on http://localhost:8001
echo - chat-service running on http://localhost:8000
echo - timezone-mcp-server running on http://localhost:8003
echo - OpenAI API key configured
echo.

REM Check if services are running
echo Checking if services are running...
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Auth service not running on port 8001
    exit /b 1
)
echo [OK] Auth service is running

curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Chat service not running on port 8000
    exit /b 1
)
echo [OK] Chat service is running

curl -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Timezone MCP server not running on port 8003
    exit /b 1
)
echo [OK] Timezone MCP server is running

echo.
echo All services are ready. Starting tests...
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the MCP integration tests
pytest test_8_mcp_integration.py -v -s --tb=short

echo.
echo ========================================
echo Test execution completed
echo ========================================
