#!/bin/bash
# Check Services Health (Mac/Linux)

echo "============================================"
echo "Checking Services Health"
echo "============================================"
echo

check_service() {
    local name=$1
    local url=$2
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
        echo "✅ $name - Running"
    else
        echo "❌ $name - Not running"
    fi
}

check_service "Auth Service     " "http://localhost:8001/docs"
check_service "Chat Service     " "http://localhost:8000/docs"
check_service "Analytics Service" "http://localhost:8002/docs"
check_service "Frontend         " "http://localhost:3000"

echo
echo "============================================"
echo "Health check complete"
echo "============================================"
echo
