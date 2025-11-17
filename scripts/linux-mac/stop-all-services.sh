#!/bin/bash
# Stop All Services (Mac/Linux)

echo "============================================"
echo "Stopping All Services"
echo "============================================"
echo

# Kill processes by port
kill_by_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Stopping $service (port $port)..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        echo "  ✅ $service stopped"
    else
        echo "  ℹ️  $service not running"
    fi
}

# Stop each service
kill_by_port 8001 "Auth Service"
kill_by_port 8000 "Chat Service"
kill_by_port 8002 "Analytics Service"
kill_by_port 3000 "Frontend"

echo
echo "============================================"
echo "✅ All services stopped"
echo "============================================"
echo
