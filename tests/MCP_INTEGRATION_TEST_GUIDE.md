# MCP Tool Integration - End-to-End Testing Guide

## Overview

This test suite validates the complete MCP (Model Context Protocol) tool integration flow in the ConvoAI chat system. It verifies that the LLM can intelligently route user queries to appropriate MCP tools when needed.

## Test Architecture

```
User Query → Chat Service → Intent Analysis (LLM) → Decision:
                                                      ├─→ Use MCP Tool → Format Result → Response
                                                      └─→ Direct LLM Response
```

## Test Coverage

### Test 1: Services Health Check
- **Purpose**: Verify all required services are running
- **Checks**: Auth service, Chat service, Timezone MCP server
- **Expected**: All services return 200 OK on `/health` endpoint

### Test 2: MCP Server Tools Endpoint
- **Purpose**: Verify MCP server exposes available tools
- **Checks**: GET `/tools` returns list of tools with descriptions
- **Expected**: At least 3 tools (get_current_time, list_timezones, convert_time)

### Test 3: Register MCP Server
- **Purpose**: Register MCP server via chat-service API
- **Checks**: POST `/mcp-servers/` with user authentication
- **Expected**: Server registered with unique ID and active status

### Test 4: List User MCP Servers
- **Purpose**: Verify user can see their registered servers
- **Checks**: GET `/mcp-servers/` returns user's servers
- **Expected**: List contains previously registered server

### Test 5: Create Conversation
- **Purpose**: Create conversation for testing chat flow
- **Checks**: POST `/conversations/` creates new conversation
- **Expected**: Conversation ID returned successfully

### Test 6: MCP Tool Discovery & Intent Analysis (CORE TEST)
- **Purpose**: Verify complete MCP tool integration flow
- **Query**: "What time is it in New York right now?"
- **Expected Flow**:
  1. User sends message
  2. Chat service discovers available MCP tools
  3. LLM analyzes intent with tool context
  4. LLM decides to use `get_current_time` tool
  5. MCP tool is called with OAuth authentication
  6. Result is formatted and returned to user
- **Validation**:
  - Message processed successfully
  - Response contains timezone information
  - Metadata indicates MCP tool was used
  - Response time is reasonable

### Test 7: Multiple Query Types
- **Purpose**: Test LLM's ability to route different query types
- **Test Cases**:
  
  | Query | Should Use MCP? | Expected Keywords |
  |-------|-----------------|-------------------|
  | "What's the current time in Tokyo?" | ✓ Yes | time, tokyo, jst |
  | "Convert 2:00 PM EST to PST" | ✓ Yes | convert, pst, time |
  | "What is the capital of France?" | ✗ No | paris, france |

- **Expected**: LLM correctly decides when to use tools vs. respond directly

### Test 8: MCP Tool Error Handling
- **Purpose**: Verify graceful error handling
- **Query**: "What time is it in InvalidTimezoneXYZ?"
- **Expected**: Error handled gracefully, helpful message returned

### Test 9: Conversation Context with MCP Tools
- **Purpose**: Verify conversation context maintained across MCP tool calls
- **Flow**:
  1. "What time is it in London?"
  2. "And what about Tokyo?" (context-dependent)
- **Expected**: Both queries answered correctly, context preserved

### Test 10: Deactivate MCP Server
- **Purpose**: Verify deactivated servers are not used
- **Flow**:
  1. Deactivate MCP server
  2. Send timezone query
  3. Verify MCP tool was NOT used
- **Expected**: LLM responds directly without using deactivated server

## Prerequisites

### Services Running
```bash
# Terminal 1: Auth Service
cd auth-service
python -m uvicorn auth_server.main:app --host 0.0.0.0 --port 8001

# Terminal 2: Chat Service
cd chat-service
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# Terminal 3: Timezone MCP Server
cd timezone-mcp-server
python http_server.py
```

### Environment Variables
```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional (defaults shown)
export AUTH_SERVICE_URL="http://localhost:8001"
export CHAT_SERVICE_URL="http://localhost:8000"
```

### Dependencies
```bash
cd tests
pip install -r requirements.txt
```

## Running the Tests

### Option 1: Run All Tests (Recommended)
```bash
# Windows
cd tests
run_mcp_test.bat

# Linux/Mac
cd tests
chmod +x run_mcp_test.sh
./run_mcp_test.sh
```

### Option 2: Run with pytest
```bash
cd tests
pytest test_8_mcp_integration.py -v -s
```

### Option 3: Run Specific Test
```bash
# Run only the core integration test
pytest test_8_mcp_integration.py::TestMCPIntegration::test_mcp_tool_discovery_and_intent_analysis -v -s

# Run only query type tests
pytest test_8_mcp_integration.py::TestMCPIntegration::test_mcp_tool_call_with_different_queries -v -s
```

### Option 4: Run Complete Flow (Manual)
```bash
pytest test_8_mcp_integration.py::run_complete_flow_test -v -s
```

## Expected Output

### Successful Test Run
```
=== Test 1: Services Health Check ===
✓ Auth Service is healthy
✓ Chat Service is healthy
✓ Timezone MCP Server is healthy

=== Test 2: MCP Server Tools Endpoint ===
✓ MCP server exposes 3 tools:
  - get_current_time: Get current time in a timezone
  - list_timezones: List all available timezones, optionally filtered
  - convert_time: Convert time between timezones

=== Test 6: MCP Tool Discovery & Intent Analysis ===
Sending query: 'What time is it in New York right now?'
Expected: LLM should detect intent and use get_current_time tool

✓ Message processed successfully
  User message ID: msg_abc123
  AI response ID: msg_def456
  Response time: 2345ms

✓ MCP Tool Integration Successful!
  Tool used: get_current_time
  Server ID: mcp_xyz789
  Tool result: {
    "success": true,
    "result": {
      "timezone": "America/New_York",
      "current_time": "2025-11-18T15:30:00-05:00",
      ...
    }
  }

📝 AI Response: The current time in New York is 3:30 PM EST...

✓ Response contains relevant timezone information

========================================
✓ ALL MCP INTEGRATION TESTS PASSED!
========================================
```

## Troubleshooting

### Services Not Running
**Error**: `[ERROR] <Service> not running on port <PORT>`

**Solution**:
1. Check if service is running: `curl http://localhost:<PORT>/health`
2. Start the service (see Prerequisites section)
3. Check logs for errors

### OpenAI API Key Not Set
**Error**: `OpenAI API authentication failed`

**Solution**:
```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Or create .env file in chat-service directory
echo "OPENAI_API_KEY=sk-..." > chat-service/.env
```

### MCP Tool Not Used
**Issue**: Test passes but `mcp_tool_used: false`

**Possible Causes**:
1. No MCP servers registered for user
2. MCP server is deactivated
3. LLM decided it could answer directly
4. MCP server discovery failed

**Debug Steps**:
1. Check MCP server registration: `curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/mcp-servers/`
2. Verify server is active and URL is correct
3. Check chat-service logs for MCP discovery errors
4. Try more explicit query (e.g., "Use the timezone tool to tell me...")

### Tool Call Failed
**Error**: `Tool execution failed: 400/401/500`

**Common Issues**:
- **401 Unauthorized**: API key not valid or expired
  - Check if user's access token is being passed correctly
  - Verify auth-service is accessible from MCP server
- **400 Bad Request**: Invalid parameters
  - Check tool parameter format
  - Verify timezone name is valid
- **500 Internal Server Error**: MCP server error
  - Check timezone-mcp-server logs
  - Verify pytz and other dependencies installed

### Context Not Maintained
**Issue**: Follow-up questions don't work

**Check**:
1. Same `conversation_id` used for both messages
2. Conversation status is "active"
3. Message history is being retrieved correctly

## Verifying the Complete Flow

To manually verify each step:

### 1. Check Tool Discovery
```bash
# Get auth token
TOKEN=$(curl -X POST http://localhost:8001/auth/token \
  -d "username=testuser&password=testpass" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  | jq -r .access_token)

# List MCP servers
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/mcp-servers/
```

### 2. Send Test Query
```bash
# Create conversation
CONV_ID=$(curl -X POST http://localhost:8000/conversations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}' \
  | jq -r .id)

# Send message
curl -X POST http://localhost:8000/messages/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"conversation_id\":\"$CONV_ID\",\"content\":\"What time is it in Tokyo?\"}" \
  | jq .
```

### 3. Check Metadata
Look for `mcp_tool_used: true` in the response metadata to confirm tool usage.

## Performance Benchmarks

Expected response times:
- **Without MCP tool**: 1-3 seconds
- **With MCP tool**: 2-5 seconds
  - Tool discovery: ~100-300ms
  - Intent analysis: ~1-2s
  - Tool execution: ~200-500ms
  - Response formatting: ~1-2s

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run MCP Integration Tests
  run: |
    docker-compose up -d
    sleep 10  # Wait for services
    cd tests
    pytest test_8_mcp_integration.py -v
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Next Steps

After all tests pass:

1. **Test with Real Users**: Deploy to staging and monitor actual usage
2. **Add More MCP Servers**: Weather, calendar, email, etc.
3. **Optimize Tool Discovery**: Cache tool definitions
4. **Improve Intent Detection**: Fine-tune system prompts
5. **Add Tool Chaining**: Allow LLM to use multiple tools in sequence
6. **Implement Streaming**: Stream MCP tool results for better UX

## References

- [MCP Server Management Documentation](../docs/MCP_SERVER_MANAGEMENT.md)
- [MCP Implementation Summary](../docs/MCP_IMPLEMENTATION_SUMMARY.md)
- [MCP Quick Start Guide](../docs/MCP_QUICKSTART.md)
- [Model Context Protocol Specification](https://github.com/modelcontextprotocol/specification)
