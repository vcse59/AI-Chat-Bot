#!/bin/bash
# Start Frontend (Mac/Linux)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT/chat-frontend"

echo "Starting React Frontend on port 3000..."
echo "Access app at: http://localhost:3000"
echo

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

npm start
