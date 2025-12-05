#!/bin/bash
# LangChain Service Startup Script for Linux/Mac

echo "================================================"
echo " LangChain Workflow Service Startup"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "[1/5] Python version check..."
python3 --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "[2/5] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo ""
    echo "[2/5] Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Install/upgrade dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file and set your OPENAI_API_KEY"
    echo "Press any key to continue..."
    read -n 1
fi

# Check if OPENAI_API_KEY is set
if grep -q "your-openai-api-key-here" .env; then
    echo ""
    echo "ERROR: OPENAI_API_KEY not configured in .env file"
    echo "Please set your OpenAI API key in .env"
    exit 1
fi

echo ""
echo "[5/5] Starting LangChain Service..."
echo ""
echo "================================================"
echo " Service Configuration:"
echo "================================================"
echo " Port: 8004"
echo " API Docs: http://localhost:8004/docs"
echo " Health: http://localhost:8004/health"
echo "================================================"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

# Start the service
python main.py
