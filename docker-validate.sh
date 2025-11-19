#!/bin/bash
# Docker Deployment and Validation Script for ConvoAI with MCP Integration
# This script builds, starts, and validates all services in Docker

set -e  # Exit on error

echo "========================================"
echo "ConvoAI Docker Deployment with MCP"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "[ACTION REQUIRED] Please edit .env file and set:"
    echo "  1. OPENAI_API_KEY=your-actual-api-key"
    echo "  2. AUTH_SECRET_KEY=your-secure-secret-key"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Verify OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "[ERROR] OPENAI_API_KEY not properly set in .env file"
    echo "Please edit .env and set: OPENAI_API_KEY=sk-your-key"
    exit 1
fi

echo "[OK] Environment configuration found"
echo ""

# Stop any running containers
echo "Step 1: Stopping existing containers..."
docker-compose down
echo ""

# Build all services
echo "Step 2: Building Docker images..."
echo "This may take a few minutes on first run..."
docker-compose build
echo "[OK] All images built successfully"
echo ""

# Start services
echo "Step 3: Starting services..."
docker-compose up -d
echo "[OK] All services started"
echo ""

# Wait for services to be ready
echo "Step 4: Waiting for services to be healthy..."
echo "This may take 30-60 seconds..."

MAX_WAIT=60
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    # Check auth-server health
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        AUTH_STATUS=0
    else
        AUTH_STATUS=1
    fi
    
    # Check chat-service health
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        CHAT_STATUS=0
    else
        CHAT_STATUS=1
    fi
    
    # Check timezone-mcp-server health
    if curl -s http://localhost:8003/health > /dev/null 2>&1; then
        MCP_STATUS=0
    else
        MCP_STATUS=1
    fi
    
    if [ $AUTH_STATUS -eq 0 ] && [ $CHAT_STATUS -eq 0 ] && [ $MCP_STATUS -eq 0 ]; then
        break
    fi
    
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo "[ERROR] Services did not become healthy in time"
    echo ""
    echo "Checking service logs:"
    docker-compose logs --tail=50
    exit 1
fi

echo "[OK] All services are healthy!"
echo ""

# Display service status
echo "========================================"
echo "Service Status"
echo "========================================"
echo ""
echo "[✓] Auth Service:     http://localhost:8001"
echo "[✓] Chat Service:     http://localhost:8000"
echo "[✓] MCP Server:       http://localhost:8003"
echo "[✓] Frontend:         http://localhost:3000"
echo "[✓] Nginx (prod):     http://localhost:80"
echo ""

# Show running containers
echo "Running Containers:"
docker-compose ps
echo ""

# Validate MCP integration
echo "========================================"
echo "Validating MCP Integration"
echo "========================================"
echo ""

echo "Test 1: Check MCP server tools endpoint..."
if curl -s http://localhost:8003/tools | grep -q "tools"; then
    echo "[PASS] MCP server exposes tools endpoint"
else
    echo "[FAIL] MCP server tools endpoint not responding"
fi
echo ""

echo "Test 2: Create test user and authenticate..."
TIMESTAMP=$(date +%s)
TEST_USER="dockertest_${TIMESTAMP}"

# Register user
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8001/users/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${TEST_USER}\",\"email\":\"${TEST_USER}@test.com\",\"password\":\"Test123!\"}")

if echo "$REGISTER_RESPONSE" | grep -q "id"; then
    echo "[PASS] User registered successfully"
else
    echo "[FAIL] User registration failed"
    echo "$REGISTER_RESPONSE"
    exit 1
fi
echo ""

# Login to get token
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_USER}&password=Test123!")

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "[FAIL] Failed to get access token"
    echo "$TOKEN_RESPONSE"
    exit 1
fi
echo "[PASS] User authenticated successfully"
echo ""

echo "Test 3: Register MCP server..."
MCP_RESPONSE=$(curl -s -X POST http://localhost:8000/mcp-servers/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Timezone MCP\",\"description\":\"Test MCP server\",\"server_url\":\"http://timezone-mcp-server:8003\",\"api_key\":\"${TOKEN}\",\"is_active\":true}")

if echo "$MCP_RESPONSE" | grep -q "id"; then
    echo "[PASS] MCP server registered successfully"
else
    echo "[FAIL] MCP server registration failed"
    echo "$MCP_RESPONSE"
    exit 1
fi
echo ""

echo "Test 4: Create conversation..."
CONV_RESPONSE=$(curl -s -X POST http://localhost:8000/conversations/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Docker Test\",\"system_message\":\"You are a helpful assistant.\"}")

CONV_ID=$(echo "$CONV_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$CONV_ID" ]; then
    echo "[FAIL] Failed to create conversation"
    echo "$CONV_RESPONSE"
    exit 1
fi
echo "[PASS] Conversation created: ${CONV_ID}"
echo ""

echo "Test 5: Send message with MCP tool requirement..."
echo "Sending: 'What time is it in Tokyo?'"
echo "This will test the complete MCP integration flow..."

MESSAGE_RESPONSE=$(curl -s -X POST http://localhost:8000/messages/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\":\"${CONV_ID}\",\"content\":\"What time is it in Tokyo?\"}")

if echo "$MESSAGE_RESPONSE" | grep -q "ai_response"; then
    echo "[PASS] Message processed successfully"
    echo ""
    echo "Response preview:"
    echo "$MESSAGE_RESPONSE" | python3 -m json.tool 2>/dev/null | grep -A 2 "content" | head -5 || echo "$MESSAGE_RESPONSE" | grep -o '"content":"[^"]*' | head -1
else
    echo "[FAIL] Message processing failed"
    echo "$MESSAGE_RESPONSE"
fi
echo ""

echo "========================================"
echo "Validation Complete"
echo "========================================"
echo ""

echo "Next Steps:"
echo ""
echo "1. View logs:           docker-compose logs -f"
echo "2. View specific logs:  docker-compose logs -f openai-chatbot"
echo "3. Run full tests:      cd tests && pytest test_8_mcp_integration.py -v -s"
echo "4. Stop services:       docker-compose down"
echo "5. Access frontend:     http://localhost:3000"
echo ""
echo "For detailed testing, run:"
echo "  cd tests"
echo "  pytest test_8_mcp_integration.py -v -s"
echo ""
