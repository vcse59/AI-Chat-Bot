@echo off
REM Test runner script for Open ChatBot E2E tests (Windows)

echo ========================================
echo Open ChatBot - End-to-End Test Suite
echo ========================================
echo.

echo [1/5] Checking if services are running...

REM Check auth-server
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo [X] Auth Server is not responding
    echo Starting services with docker-compose...
    docker-compose up -d
    timeout /t 10 /nobreak >nul
) else (
    echo [OK] Auth Server is ready
)

REM Check chat-api
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [X] Chat API is not responding
    exit /b 1
) else (
    echo [OK] Chat API is ready
)

REM Check frontend
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [!] Frontend is not responding (optional)
) else (
    echo [OK] Frontend is ready
)

echo.

echo [2/5] Installing test dependencies...
pip install -r tests\requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to install dependencies
    exit /b 1
) else (
    echo [OK] Dependencies installed
)

echo.

echo [3/5] Running tests...
echo.

if "%1"=="auth" (
    echo Running Authentication ^& Authorization tests...
    pytest tests\test_1_auth_service.py -v
) else if "%1"=="chat" (
    echo Running Chat API tests...
    pytest tests\test_2_chat_api.py -v
) else if "%1"=="websocket" (
    echo Running WebSocket tests...
    pytest tests\test_3_websocket.py -v
) else if "%1"=="e2e" (
    echo Running End-to-End integration tests...
    pytest tests\test_4_end_to_end.py -v
) else if "%1"=="coverage" (
    echo Running all tests with coverage...
    pytest tests\ -v --cov=. --cov-report=html --cov-report=term
) else if "%1"=="report" (
    echo Running all tests and generating HTML report...
    pytest tests\ -v --html=test_report.html --self-contained-html
) else (
    echo Running all tests...
    pytest tests\ -v
)

set TEST_EXIT_CODE=%errorlevel%

echo.
echo [4/5] Test execution completed
echo.

if %TEST_EXIT_CODE%==0 (
    echo ========================================
    echo [OK] ALL TESTS PASSED
    echo ========================================
) else (
    echo ========================================
    echo [X] SOME TESTS FAILED
    echo ========================================
)

echo.
echo [5/5] Usage examples:
echo   run_tests.bat           # Run all tests
echo   run_tests.bat auth      # Run authentication tests only
echo   run_tests.bat chat      # Run chat API tests only
echo   run_tests.bat websocket # Run WebSocket tests only
echo   run_tests.bat e2e       # Run end-to-end tests only
echo   run_tests.bat coverage  # Run with coverage report
echo   run_tests.bat report    # Generate HTML report

exit /b %TEST_EXIT_CODE%
