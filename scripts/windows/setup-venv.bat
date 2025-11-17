@echo off
echo ========================================
echo Setting up Virtual Environments
echo ========================================
echo.

REM Create virtual environments for each service
echo Creating virtual environment for Auth Service...
cd /d "%~dp0..\..\auth-service"
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install poetry
poetry install
call venv\Scripts\deactivate
echo ✅ Auth Service venv created
echo.

echo Creating virtual environment for Chat Service...
cd /d "%~dp0..\..\openai_web_service"
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate
echo ✅ Chat Service venv created
echo.

echo Creating virtual environment for Analytics Service...
cd /d "%~dp0..\..\analytics-service"
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install poetry
poetry install
call venv\Scripts\deactivate
echo ✅ Analytics Service venv created
echo.

echo Creating virtual environment for Tests...
cd /d "%~dp0..\..\tests"
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate
echo ✅ Tests venv created
echo.

echo ========================================
echo All virtual environments created!
echo ========================================
echo.
pause
