#!/bin/bash
# Start Chat Service (Mac/Linux)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT/chat-service"

echo "Starting Chat Service on port 8000..."
echo "Access API docs at: http://localhost:8000/docs"
echo

source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

