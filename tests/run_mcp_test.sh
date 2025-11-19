#!/bin/bash
# Quick test runner for MCP Integration tests
# Make sure all services are running before executing this script

echo "========================================"
echo "MCP Integration Test Runner"
echo "========================================"
echo ""
echo "Prerequisites:"
echo "- auth-service running on http://localhost:8001"
echo "- chat-service running on http://localhost:8000"
echo "- timezone-mcp-server running on http://localhost:8003"
echo "- OpenAI API key configured"
echo ""

# Check if services are running
echo "Checking if services are running..."
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "[ERROR] Auth service not running on port 8001"
    exit 1
fi
echo "[OK] Auth service is running"

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "[ERROR] Chat service not running on port 8000"
    exit 1
fi
echo "[OK] Chat service is running"

if ! curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo "[ERROR] Timezone MCP server not running on port 8003"
    exit 1
fi
echo "[OK] Timezone MCP server is running"

echo ""
echo "All services are ready. Starting tests..."
echo ""

# Activate virtual environment if exists
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

# Run the MCP integration tests
pytest test_8_mcp_integration.py -v -s --tb=short

echo ""
echo "========================================"
echo "Test execution completed"
echo "========================================"
