#!/bin/bash
# Test runner script for Open ChatBot E2E tests

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Open ChatBot - End-to-End Test Suite${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Check if services are running
echo -e "${YELLOW}[1/5] Checking if services are running...${NC}"

if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}✗ Services are not running!${NC}"
    echo -e "${YELLOW}Starting services with docker-compose...${NC}"
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
fi

# Check auth-server
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Auth Server is ready${NC}"
else
    echo -e "${RED}✗ Auth Server is not responding${NC}"
    exit 1
fi

# Check chat-api
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Chat API is ready${NC}"
else
    echo -e "${RED}✗ Chat API is not responding${NC}"
    exit 1
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is ready${NC}"
else
    echo -e "${YELLOW}⚠ Frontend is not responding (optional)${NC}"
fi

echo ""

# Install dependencies
echo -e "${YELLOW}[2/5] Installing test dependencies...${NC}"
pip install -r tests/requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

echo ""

# Run tests based on argument
echo -e "${YELLOW}[3/5] Running tests...${NC}"
echo ""

case "$1" in
    auth)
        echo -e "${YELLOW}Running Authentication & Authorization tests...${NC}"
        pytest tests/test_1_auth_service.py -v
        ;;
    chat)
        echo -e "${YELLOW}Running Chat API tests...${NC}"
        pytest tests/test_2_chat_api.py -v
        ;;
    websocket)
        echo -e "${YELLOW}Running WebSocket tests...${NC}"
        pytest tests/test_3_websocket.py -v
        ;;
    e2e)
        echo -e "${YELLOW}Running End-to-End integration tests...${NC}"
        pytest tests/test_4_end_to_end.py -v
        ;;
    coverage)
        echo -e "${YELLOW}Running all tests with coverage...${NC}"
        pytest tests/ -v --cov=. --cov-report=html --cov-report=term
        ;;
    report)
        echo -e "${YELLOW}Running all tests and generating HTML report...${NC}"
        pytest tests/ -v --html=test_report.html --self-contained-html
        ;;
    *)
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest tests/ -v
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
echo -e "${YELLOW}[4/5] Test execution completed${NC}"
echo ""

# Summary
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo -e "${RED}========================================${NC}"
fi

echo ""
echo -e "${YELLOW}[5/5] Usage examples:${NC}"
echo "  ./run_tests.sh          # Run all tests"
echo "  ./run_tests.sh auth     # Run authentication tests only"
echo "  ./run_tests.sh chat     # Run chat API tests only"
echo "  ./run_tests.sh websocket # Run WebSocket tests only"
echo "  ./run_tests.sh e2e      # Run end-to-end tests only"
echo "  ./run_tests.sh coverage # Run with coverage report"
echo "  ./run_tests.sh report   # Generate HTML report"

exit $TEST_EXIT_CODE
