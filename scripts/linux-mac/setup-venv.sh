#!/bin/bash
# Setup Virtual Environments Script (Mac/Linux)
# Creates Python virtual environments for all services

set -e  # Exit on error

echo "============================================"
echo "Setting up Virtual Environments"
echo "============================================"
echo

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 1. Auth Service
echo "1. Setting up Auth Service virtual environment..."
cd "$PROJECT_ROOT/auth-service"
if [ -d "venv" ]; then
    echo "   Removing existing venv..."
    rm -rf venv
fi
python3 -m venv venv
echo "   Virtual environment created"
echo "   Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install poetry
poetry install
deactivate
echo "   ✅ Auth Service venv ready"
echo

# 2. Chat Service (OpenAI Web Service)
echo "2. Setting up Chat Service virtual environment..."
cd "$PROJECT_ROOT/chat-service"
if [ -d "venv" ]; then
    echo "   Removing existing venv..."
    rm -rf venv
fi
python3 -m venv venv
echo "   Virtual environment created"
echo "   Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "   ✅ Chat Service venv ready"
echo

# 3. Analytics Service
echo "3. Setting up Analytics Service virtual environment..."
cd "$PROJECT_ROOT/analytics-service"
if [ -d "venv" ]; then
    echo "   Removing existing venv..."
    rm -rf venv
fi
python3 -m venv venv
echo "   Virtual environment created"
echo "   Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install poetry
poetry install
deactivate
echo "   ✅ Analytics Service venv ready"
echo

# 4. Tests
echo "4. Setting up Tests virtual environment..."
cd "$PROJECT_ROOT/tests"
if [ -d "venv" ]; then
    echo "   Removing existing venv..."
    rm -rf venv
fi
python3 -m venv venv
echo "   Virtual environment created"
echo "   Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "   ✅ Tests venv ready"
echo

cd "$PROJECT_ROOT"
echo "============================================"
echo "✅ All virtual environments are ready!"
echo "============================================"
echo
echo "Next steps:"
echo "  1. Run: ./scripts/start-all-services.sh"
echo "  2. Access the app at http://localhost:3000"
echo

