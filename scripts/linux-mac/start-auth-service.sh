#!/bin/bash
# Start Auth Service (Mac/Linux)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT/auth-service"

echo "Starting Auth Service on port 8001..."
echo "Access API docs at: http://localhost:8001/docs"
echo

source venv/bin/activate
python -m uvicorn auth_server.main:app --host 0.0.0.0 --port 8001 --reload
