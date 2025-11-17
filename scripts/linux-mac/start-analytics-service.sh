#!/bin/bash
# Start Analytics Service (Mac/Linux)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT/analytics-service"

echo "Starting Analytics Service on port 8002..."
echo "Access API docs at: http://localhost:8002/docs"
echo

source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
