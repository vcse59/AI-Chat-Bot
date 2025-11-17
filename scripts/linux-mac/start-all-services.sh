#!/bin/bash
# Start All Services (Mac/Linux)
# Opens each service in a new terminal window

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

echo "============================================"
echo "Starting All Services"
echo "============================================"
echo

# Detect OS and use appropriate terminal command
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Starting services on macOS..."
    
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_ROOT' && ./scripts/start-auth-service.sh"
    do script "cd '$PROJECT_ROOT' && sleep 2 && ./scripts/start-chat-service.sh"
    do script "cd '$PROJECT_ROOT' && sleep 4 && ./scripts/start-analytics-service.sh"
    do script "cd '$PROJECT_ROOT' && sleep 6 && ./scripts/start-frontend.sh"
end tell
EOF

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Starting services on Linux..."
    
    # Try different terminal emulators
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT' && ./scripts/start-auth-service.sh; exec bash"
        sleep 2
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT' && ./scripts/start-chat-service.sh; exec bash"
        sleep 2
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT' && ./scripts/start-analytics-service.sh; exec bash"
        sleep 2
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT' && ./scripts/start-frontend.sh; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$PROJECT_ROOT' && ./scripts/start-auth-service.sh" &
        sleep 2
        xterm -e "cd '$PROJECT_ROOT' && ./scripts/start-chat-service.sh" &
        sleep 2
        xterm -e "cd '$PROJECT_ROOT' && ./scripts/start-analytics-service.sh" &
        sleep 2
        xterm -e "cd '$PROJECT_ROOT' && ./scripts/start-frontend.sh" &
    elif command -v konsole &> /dev/null; then
        konsole -e bash -c "cd '$PROJECT_ROOT' && ./scripts/start-auth-service.sh; exec bash" &
        sleep 2
        konsole -e bash -c "cd '$PROJECT_ROOT' && ./scripts/start-chat-service.sh; exec bash" &
        sleep 2
        konsole -e bash -c "cd '$PROJECT_ROOT' && ./scripts/start-analytics-service.sh; exec bash" &
        sleep 2
        konsole -e bash -c "cd '$PROJECT_ROOT' && ./scripts/start-frontend.sh; exec bash" &
    else
        echo "No supported terminal emulator found."
        echo "Please start services manually:"
        echo "  Terminal 1: ./scripts/start-auth-service.sh"
        echo "  Terminal 2: ./scripts/start-chat-service.sh"
        echo "  Terminal 3: ./scripts/start-analytics-service.sh"
        echo "  Terminal 4: ./scripts/start-frontend.sh"
        exit 1
    fi
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo
echo "✅ All services are starting..."
echo
echo "Services:"
echo "  • Auth Service:      http://localhost:8001"
echo "  • Chat Service:      http://localhost:8000"
echo "  • Analytics Service: http://localhost:8002"
echo "  • Frontend:          http://localhost:3000"
echo
echo "Press Ctrl+C in each terminal window to stop services"
echo
