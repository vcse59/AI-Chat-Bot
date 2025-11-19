# Timezone MCP Server

A Model Context Protocol (MCP) server that provides timezone-related tools for AI assistants. This server allows AI agents to fetch current time in any timezone around the world.

## Features

- **Get Current Time**: Retrieve the current time in any timezone
- **JSON-RPC 2.0 Protocol**: Implements the MCP standard for tool discovery and execution
- **OAuth Authentication**: Supports Bearer token authentication for secure access
- **Health Check Endpoint**: Monitor server availability

## API Endpoints

### Health Check
```bash
GET /health
```
Returns server status and uptime.

### MCP Endpoint
```bash
POST /mcp
Content-Type: application/json
Authorization: Bearer <token>
```

## MCP Tools

### 1. get_current_time
Get the current time in a specified timezone.

**Parameters:**
- `timezone` (string, required): IANA timezone identifier (e.g., "America/New_York", "Europe/London", "Asia/Tokyo")

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_current_time",
    "arguments": {
      "timezone": "America/New_York"
    }
  }
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "The current time in America/New_York is: 2025-11-18 22:30:45 EST"
      }
    ]
  }
}
```

## Tool Discovery

### tools/list
Discover available tools on this MCP server.

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_current_time",
        "description": "Get the current time in a specified timezone",
        "inputSchema": {
          "type": "object",
          "properties": {
            "timezone": {
              "type": "string",
              "description": "IANA timezone identifier (e.g., 'America/New_York', 'Europe/London')"
            }
          },
          "required": ["timezone"]
        }
      }
    ]
  }
}
```

## Running the Server

### Option 1: With Docker Compose (Recommended)
```bash
# From project root
docker-compose up timezone-mcp-server
```

### Option 2: Standalone with Docker
```bash
# From timezone-mcp-server directory
docker build -t timezone-mcp-server .
docker run -p 8003:8003 timezone-mcp-server
```

### Option 3: On Host Machine (Local Development)

**Prerequisites:**
- Python 3.12+
- Terminal/Command Prompt

**Setup Steps:**

1. **Navigate to timezone-mcp-server directory**
   ```bash
   cd timezone-mcp-server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment** (optional - create `.env` file)
   ```env
   HOST=0.0.0.0
   PORT=8003
   LOG_LEVEL=info
   ```

6. **Start the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8003 --reload
   ```

7. **Verify server is running**
   - Health Check: http://localhost:8003/health
   - MCP Endpoint: http://localhost:8003/mcp

**Development Mode:**
```bash
# With auto-reload for development
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Production Mode:**
```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn main:app --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8003
```

**Common Issues:**

```bash
# Port already in use
uvicorn main:app --host 0.0.0.0 --port 8013

# Import errors
pip install -r requirements.txt

# Timezone errors
pip install pytz
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8003 |
| `HOST` | Server host | 0.0.0.0 |
| `LOG_LEVEL` | Logging level | info |

## Authentication

The server supports Bearer token authentication. Include the token in the Authorization header:

```bash
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

When integrated with the chat application, user authentication tokens are automatically passed to the MCP server.

## Integration with Chat Application

### Register MCP Server
1. Navigate to MCP Server Management in the chat application
2. Click "Add MCP Server"
3. Fill in details:
   - **Name**: Timezone Server
   - **Description**: Get current time in any timezone
   - **Server URL**: `http://timezone-mcp-server:8003/mcp`
   - **Active**: ✓
4. Click "Create Server"

The chat application will automatically use your authentication token when calling this MCP server.

### Example Usage
Once registered, users can ask timezone-related questions:
- "What time is it in Tokyo?"
- "What's the current time in London?"
- "Tell me the time in New York"

The AI assistant will automatically use the `get_current_time` tool to fetch real-time data.

## Supported Timezones

This server supports all IANA timezone identifiers. Common examples:

**Americas:**
- America/New_York (EST/EDT)
- America/Chicago (CST/CDT)
- America/Los_Angeles (PST/PDT)
- America/Toronto
- America/Sao_Paulo

**Europe:**
- Europe/London (GMT/BST)
- Europe/Paris (CET/CEST)
- Europe/Berlin
- Europe/Moscow

**Asia:**
- Asia/Tokyo (JST)
- Asia/Shanghai (CST)
- Asia/Dubai
- Asia/Kolkata (IST)
- Asia/Singapore

**Oceania:**
- Australia/Sydney (AEST/AEDT)
- Pacific/Auckland

For a complete list, see: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## Error Handling

### Invalid Timezone
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid timezone: InvalidTimezone"
  }
}
```

### Missing Parameters
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Missing required parameter: timezone"
  }
}
```

### Authentication Error
```
HTTP 401 Unauthorized
```

## Development

### Project Structure
```
timezone-mcp-server/
├── main.py              # FastAPI application and MCP implementation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
└── README.md           # This file
```

### Adding New Tools

1. Define the tool schema in `tools/list` response
2. Implement the tool logic in `tools/call` handler
3. Update documentation

Example:
```python
async def handle_tools_call(call_params: dict):
    tool_name = call_params.get("name")
    arguments = call_params.get("arguments", {})
    
    if tool_name == "your_new_tool":
        # Implement your tool logic
        result = your_tool_function(**arguments)
        return {
            "content": [
                {"type": "text", "text": result}
            ]
        }
```

### Testing

Test tool discovery:
```bash
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Test tool execution:
```bash
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"tools/call",
    "params":{
      "name":"get_current_time",
      "arguments":{"timezone":"America/New_York"}
    }
  }'
```

## MCP Protocol Compliance

This server implements the Model Context Protocol (MCP) specification:
- JSON-RPC 2.0 transport
- Tool discovery via `tools/list`
- Tool execution via `tools/call`
- Structured responses with content arrays
- Standard error codes

## License

This project is part of the AI Chat Bot application.

## Related Documentation

- [Main Application README](../README.md)
- [MCP Integration Guide](../MCP_README.md)
- [Chat Service Documentation](../openai_web_service/README.md)
