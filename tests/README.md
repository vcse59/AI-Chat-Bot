# End-to-End Test Suite for Open ChatBot

This directory contains comprehensive end-to-end tests for the entire Open ChatBot application stack.

## Test Coverage

### 1. Authentication & Authorization Service Tests (`test_1_auth_service.py`)
- ✅ User Registration
  - New user registration
  - Duplicate username handling
  - Default role assignment
  - Email validation
- ✅ User Authentication
  - Successful login
  - Wrong password handling
  - Non-existent user handling
  - Empty password handling
- ✅ User Management
  - Get current user
  - Get user by username
  - Update user email
  - Update user password
- ✅ Role-Based Access Control
  - Admin list all users
  - Regular user restrictions
  - Admin delete users
  - Regular user cannot delete
- ✅ Health Check

### 2. Chat API Service Tests (`test_2_chat_api.py`)
- ✅ Conversation Management
  - Create conversation
  - List conversations
  - Get conversation by ID
  - Update conversation
  - Delete conversation
  - Unauthorized access prevention
- ✅ Message Handling
  - Send message to conversation
  - Get conversation messages
  - Unauthorized message prevention
- ✅ Chat Service Health
  - Health endpoint
  - Root endpoint
  - Chat health endpoint
- ✅ User Isolation
  - Conversations are user-specific
  - Users cannot access other's conversations

### 3. WebSocket Tests (`test_3_websocket.py`)
- ✅ WebSocket Connection
  - Anonymous connection
  - Authenticated connection
  - Invalid token rejection
  - Token-user mismatch prevention
- ✅ WebSocket Messaging
  - Start conversation via WebSocket
  - Send message via WebSocket
  - End conversation via WebSocket
- ✅ WebSocket Reconnection
  - Reconnect to same conversation
  - Multiple simultaneous connections

### 4. End-to-End Integration Tests (`test_4_end_to_end.py`)
- ✅ Complete User Journey (REST API)
  - Register → Login → Create Conversation → Send Message → Get History → Update → Delete
- ✅ Complete User Journey (WebSocket)
  - Register → Login → Connect → Start Conversation → Send Message → End → Disconnect
- ✅ Multi-User Scenarios
  - Multiple users with separate conversations
- ✅ Error Recovery
  - Invalid conversation ID
  - Unauthorized access
  - Expired token handling
  - Malformed request data
- ✅ Performance Tests
  - Multiple conversation creation
  - Rapid message sending

## Prerequisites

Before running tests, ensure all services are running:

```bash
# Start all services using Docker Compose
docker-compose up -d

# Wait for services to be ready (health checks will pass)
# - auth-server: http://localhost:8001/health
# - openai-chatbot: http://localhost:8000/health
# - chat-frontend: http://localhost:3000
```

## Installation

Install test dependencies:

```bash
# From the tests directory
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
# From the project root
pytest tests/ -v

# Or from tests directory
pytest -v
```

### Run Specific Test Files

```bash
# Authentication tests only
pytest tests/test_1_auth_service.py -v

# Chat API tests only
pytest tests/test_2_chat_api.py -v

# WebSocket tests only
pytest tests/test_3_websocket.py -v

# End-to-end tests only
pytest tests/test_4_end_to_end.py -v
```

### Run Specific Test Classes

```bash
# Run only user registration tests
pytest tests/test_1_auth_service.py::TestUserRegistration -v

# Run only WebSocket messaging tests
pytest tests/test_3_websocket.py::TestWebSocketMessaging -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term

# View coverage report
# Open htmlcov/index.html in browser
```

### Run with HTML Report

```bash
# Generate HTML test report
pytest tests/ --html=report.html --self-contained-html

# Open report.html in browser
```

### Run with JSON Report

```bash
# Generate JSON report for CI/CD
pytest tests/ --json-report --json-report-file=report.json
```

## Environment Configuration

Tests use the following default service URLs:

- **Auth Service**: `http://localhost:8001`
- **Chat Service**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`

You can override these with environment variables:

```bash
export AUTH_SERVICE_URL=http://your-auth-url:8001
export CHAT_SERVICE_URL=http://your-chat-url:8000
export FRONTEND_URL=http://your-frontend-url:3000

pytest tests/ -v
```

## Test Output

### Successful Test Run

```
tests/test_1_auth_service.py::TestUserRegistration::test_register_new_user PASSED
tests/test_1_auth_service.py::TestUserAuthentication::test_login_success PASSED
tests/test_2_chat_api.py::TestConversationManagement::test_create_conversation PASSED
tests/test_3_websocket.py::TestWebSocketConnection::test_websocket_connection_with_auth PASSED
tests/test_4_end_to_end.py::TestCompleteUserJourney::test_full_user_journey_rest_api PASSED

========================= 50 passed in 45.23s =========================
```

### Common Issues

#### Services Not Ready
```
Error: auth-server did not become ready in time
```
**Solution**: Ensure Docker containers are running and healthy:
```bash
docker-compose ps
docker-compose logs auth-server
```

#### WebSocket Timeout
```
WebSocket response timeout - server may not be configured for this test
```
**Solution**: Some WebSocket tests may be skipped if the server implementation differs. This is expected behavior.

#### Connection Refused
```
requests.exceptions.ConnectionError: Connection refused
```
**Solution**: Check that services are accessible:
```bash
curl http://localhost:8001/health
curl http://localhost:8000/health
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Compose
        run: docker-compose up -d
      
      - name: Wait for services
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:8001/health; do sleep 2; done'
          timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
      
      - name: Install test dependencies
        run: pip install -r tests/requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v --cov=. --json-report --html=report.html
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            report.html
            report.json
```

## Test Data Cleanup

Tests automatically create unique users with timestamps to avoid conflicts. However, if you want to clean up test data:

```bash
# Stop all services
docker-compose down

# Remove volumes (this deletes all databases)
docker-compose down -v

# Restart fresh
docker-compose up -d
```

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -vv -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Run Last Failed Tests

```bash
pytest tests/ --lf
```

### Debug Specific Test

```bash
pytest tests/test_1_auth_service.py::TestUserRegistration::test_register_new_user -vv -s
```

### Print Service Logs During Test

```bash
# In another terminal
docker-compose logs -f auth-server
docker-compose logs -f openai-chatbot-api
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Add docstrings explaining what is tested
4. Use fixtures for common setup
5. Clean up test data (tests create unique users automatically)
6. Update this README with new test coverage

## Test Metrics

- **Total Test Cases**: 50+
- **Test Files**: 4
- **Test Classes**: 15+
- **Average Test Duration**: ~45 seconds (all tests)
- **Coverage Target**: >80%

## License

Same as main project license.
