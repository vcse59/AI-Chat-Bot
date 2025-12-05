# Model Context Protocol (MCP) Integration Guide

## Overview

ConvoAI supports **Model Context Protocol (MCP) server integration**, allowing users to register custom MCP servers and extend the AI's capabilities with external tools and APIs through OpenAI's function calling.

## Features

- ✅ **User-Friendly UI**: Register MCP servers through the web interface
- ✅ **Automatic Authentication**: User tokens are automatically passed to MCP servers
- ✅ **Tool Discovery**: Automatic discovery of tools from registered servers
- ✅ **OpenAI Integration**: Tools are seamlessly passed to OpenAI using function calling
- ✅ **Per-User Configuration**: Each user manages their own MCP servers
- ✅ **Active/Inactive Toggle**: Enable or disable servers without deleting them

## How It Works

### Architecture Flow

```
User ─┬─► Web UI (MCP Server Manager)
      │     └─► Register MCP Server (Name, URL)
      │
      └─► Chat Interface
            └─► Send Message ──► Chat Service
                                   ├─► Discover Tools from Active MCP Servers
                                   ├─► Convert Tools to OpenAI Functions
                                   ├─► Call OpenAI API with Available Functions
                                   └─► If function_call returned:
                                         ├─► Execute MCP Tool (with user token)
                                         └─► Send result back to OpenAI
```

### Authentication Flow

1. **User logs in** → Receives JWT token from auth-service
2. **Token stored** in browser's localStorage
3. **User registers MCP server** (no manual auth credentials needed)
4. **During chat**:
   - User token automatically included in WebSocket connection
   - Chat service passes token to `mcp_tools_service`
   - Token sent as `Authorization: Bearer <token>` to MCP servers
5. **MCP servers** validate the token and execute tools securely

## Registering an MCP Server

### Via Web Interface

1. **Log in** to the platform (http://localhost:3000)

2. **Click the "MCP Servers" button** in the chat interface

3. **Click "Register MCP Server"**

4. **Fill in the form**:
   - **Name**: Descriptive name (e.g., "Timezone Service")
   - **Description**: Optional description of what the server does
   - **Server URL**: The MCP server endpoint
     - For Docker services: `http://service-name:port/mcp`
     - Example: `http://timezone-mcp-server:8003/mcp`
   - **Active**: Check to enable the server immediately

5. **Click "Register Server"**

### Example: Built-in Timezone MCP Server

ConvoAI includes a reference implementation timezone MCP server.

**Registration Details**:
- **Name**: `Timezone Service`
- **Description**: `Get current time for any timezone worldwide`
- **Server URL**: `http://timezone-mcp-server:8003/mcp`
- **Active**: ✓ (Checked)

**Test Queries**:
- "What time is it in Tokyo?"
- "Tell me the current time in New York"
- "What's the time in London right now?"
- "Show me the time in Sydney"

The AI will automatically discover and use the `get_current_time` tool to answer.

## Creating Your Own MCP Server

### MCP Server Requirements

Your custom MCP server must:
1. **Accept JSON-RPC 2.0 requests** over HTTP POST
2. **Implement `tools/list` method** to advertise available tools
3. **Implement `tools/call` method** for tool execution
4. **Accept and validate JWT tokens** from the `Authorization` header
5. **Return MCP-compliant responses** with proper error handling

### Example MCP Server (Python)

```python
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import jwt
from typing import Optional

app = FastAPI()

# JWT Secret (same as AUTH_SECRET_KEY in platform)
SECRET_KEY = "your-secret-key-here"

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: dict

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Optional[dict] = None
    error: Optional[dict] = None

def verify_token(authorization: str):
    """Verify JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/mcp")
async def handle_jsonrpc(
    request: JSONRPCRequest,
    authorization: Optional[str] = Header(None)
):
    """Handle JSON-RPC requests"""
    
    # Verify authentication
    user = verify_token(authorization)
    
    # Handle tools/list request
    if request.method == "tools/list":
        return JSONRPCResponse(
            id=request.id,
            result={
                "tools": [
                    {
                        "name": "my_tool",
                        "description": "Description of what my tool does",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "param1": {
                                    "type": "string",
                                    "description": "Description of param1"
                                }
                            },
                            "required": ["param1"]
                        }
                    }
                ]
            }
        )
    
    # Handle tool execution
    elif request.method == "tools/call":
        tool_name = request.params.get("name")
        tool_args = request.params.get("arguments", {})
        
        if tool_name == "my_tool":
            # Execute your tool logic here
            result = execute_my_tool(tool_args)
            return JSONRPCResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": result}]}
            )
    
    # Unknown method
    return JSONRPCResponse(
        id=request.id,
        error={"code": -32601, "message": "Method not found"}
    )

def execute_my_tool(args):
    """Your tool implementation"""
    param1 = args.get("param1")
    return f"Tool executed with param1={param1}"
```

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
```

**Add to docker-compose.yml**:
```yaml
my-mcp-server:
  build: ./my-mcp-server
  container_name: my-mcp-server
  ports:
    - "8004:8003"
  environment:
    - AUTH_SECRET_KEY=${AUTH_SECRET_KEY}
  networks:
    - convoai-network
  restart: unless-stopped
```

### Register in ConvoAI

After deploying your server, register it in the UI:
- **Name**: `My Custom MCP Server`
- **Description**: `Brief description of your server's capabilities`
- **Server URL**: `http://my-mcp-server:8003/mcp`
- **Active**: ✓ (Checked)

## Tool Schema Format

Tools must follow the OpenAI function calling schema:

```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "parameters": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string|number|boolean|array|object",
        "description": "Parameter description",
        "enum": ["optional", "enum", "values"]
      }
    },
    "required": ["param_name"]
  }
}
```

## Troubleshooting

### MCP Server Not Being Called

1. **Check server is registered and active**:
   - Go to MCP Servers page
   - Verify server is marked as "Active"

2. **Verify server URL**:
   - Use Docker service names for internal communication
   - Example: `http://my-mcp-server:8003/mcp` (NOT `http://localhost:8003/mcp`)

3. **Check logs**:
   ```bash
   docker logs chat-service --tail 50
   ```
   Look for:
   - `Discovered X MCP servers with tools for user`
   - `OpenAI requested function call: tool_name`
   - `Calling MCP tool: tool_name with arguments`

4. **Test MCP server directly**:
   ```bash
   # Get your auth token from browser localStorage
   TOKEN="your-jwt-token-here"
   
   curl http://localhost:8003/mcp \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/list",
       "params": {}
     }'
   ```

### Connection Failed Errors

```
ERROR:services.mcp_tools_service:Error discovering tools from MyServer: All connection attempts failed
```

**Common Causes**:
- Incorrect server URL
- MCP server not running
- MCP server not accessible from chat-service container
- Network connectivity issues
- Firewall blocking connection

**Solutions**:
1. **Verify server is running**: `docker ps | grep my-mcp-server`
2. **Check Docker network**: `docker network inspect convoai-network`
3. **Use service names, not localhost**: 
   - ✅ Correct: `http://my-mcp-server:8003/mcp`
   - ❌ Wrong: `http://localhost:8003/mcp`
4. **Test connectivity**: 
   ```bash
   docker exec chat-service curl http://my-mcp-server:8003/mcp
   ```

### Tools Not Appearing in Chat

**Check tool discovery logs**:
```bash
docker logs chat-service --tail 100 | grep "Discovered.*MCP servers"
```

**Expected output**:
```
INFO:services.mcp_tools_service:Discovered 1 MCP servers with tools for user <user_id>
```

**If seeing "Discovered 0 MCP servers"**:
1. **User token issue**: Token not being passed via WebSocket
2. **Server unreachable**: Check server URL and network connectivity
3. **Server error**: MCP server returning error on `tools/list` request
4. **Server inactive**: Verify server is marked as active in UI
5. **Authentication failure**: MCP server rejecting the user token

### Authentication Errors (401)

```
ERROR: MCP server returned 401 Unauthorized
```

**Causes**:
- User token not being passed to MCP server
- MCP server using wrong SECRET_KEY
- Token expired

**Solutions**:
1. Verify `AUTH_SECRET_KEY` is same in all services
2. Check token is being sent: Add logging in MCP server
3. Verify token validation logic in MCP server

## Best Practices

### Security
- ✅ **Always validate JWT tokens** in your MCP server
- ✅ **Use the same `AUTH_SECRET_KEY`** as ConvoAI auth-service
- ✅ **Implement rate limiting** to prevent abuse
- ✅ **Sanitize and validate** all input parameters
- ✅ **Log tool executions** for audit trails and debugging
- ✅ **Use HTTPS** for production MCP servers
- ✅ **Implement error handling** to avoid exposing sensitive information

### Performance
- ✅ **Keep tool execution fast** (<5 seconds ideal)
- ✅ **Return errors quickly** if tool can't execute
- ✅ **Implement caching** for expensive operations
- ✅ **Use async/await** for I/O-bound operations
- ✅ **Connection pooling** for database/API calls
- ✅ **Timeout handling** for external API calls

### Usability
- ✅ **Clear, descriptive tool names** (use snake_case)
- ✅ **Detailed parameter descriptions** with examples
- ✅ **Proper JSON Schema** for parameters
- ✅ **User-friendly error messages** (not stack traces)
- ✅ **Test with various inputs** including edge cases
- ✅ **Document return value format** clearly

## Example Use Cases

### 1. Weather Service
```python
{
  "name": "get_weather",
  "description": "Get current weather for a city",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {"type": "string", "description": "City name"}
    },
    "required": ["city"]
  }
}
```

### 2. Database Query
```python
{
  "name": "query_database",
  "description": "Query company database",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "SQL query"}
    },
    "required": ["query"]
  }
}
```

### 3. File Operations
```python
{
  "name": "read_file",
  "description": "Read contents of a file",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "File path"}
    },
    "required": ["path"]
  }
}
```

## API Reference

### Backend MCP Integration

**Service Location**: `chat-service/services/mcp_tools_service.py`

**Key Methods**:
- `get_available_tools(user_id: str, user_token: str)` - Discovers tools from all active MCP servers for user
- `call_tool(server_id: str, tool_name: str, arguments: dict, user_token: str)` - Executes a specific tool
- `_discover_server_tools(server: MCPServer, user_token: str)` - Calls `tools/list` on MCP server
- `_call_tool_on_server(server: MCPServer, tool_name: str, arguments: dict, user_token: str)` - Calls `tools/call`

**Database**: `chat-service/engine/models.py`

**MCPServer Model**:
```python
class MCPServer(Base):
    id = Column(String(12), primary_key=True)
    user_id = Column(String(16), ForeignKey("users.id"))
    name = Column(String(255))
    description = Column(Text)
    server_url = Column(String(500))
    auth_type = Column(String(50), default="none")
    api_key = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    config = Column(JSON)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
```

### REST API Endpoints

**Base URL**: `http://localhost:8000/api`

**Authentication**: All endpoints require `Authorization: Bearer <token>` header

#### List MCP Servers
```http
GET /mcp-servers/
Query Parameters:
  - active_only: boolean (optional, default: false)
  - skip: integer (optional, default: 0)
  - limit: integer (optional, default: 100)

Response: Array<MCPServerResponse>
Status: 200 OK
```

#### Create MCP Server
```http
POST /mcp-servers/
Headers:
  - Content-Type: application/json
  - Authorization: Bearer <token>
  
Body: {
  "name": "string" (required),
  "description": "string" (optional),
  "server_url": "string" (required),
  "is_active": boolean (optional, default: true)
}

Response: MCPServerResponse
Status: 201 Created
```

#### Get MCP Server
```http
GET /mcp-servers/{server_id}

Response: MCPServerResponse
Status: 200 OK | 404 Not Found
```

#### Update MCP Server
```http
PUT /mcp-servers/{server_id}
Headers:
  - Content-Type: application/json
  - Authorization: Bearer <token>
  
Body: {
  "name": "string" (optional),
  "description": "string" (optional),
  "server_url": "string" (optional),
  "is_active": boolean (optional)
}

Response: MCPServerResponse
Status: 200 OK | 404 Not Found
```

#### Delete MCP Server
```http
DELETE /mcp-servers/{server_id}

Response: {"message": "MCP server deleted successfully"}
Status: 200 OK | 404 Not Found
```

**MCPServerResponse Schema**:
```json
{
  "id": "string",
  "user_id": "string",
  "name": "string",
  "description": "string | null",
  "server_url": "string",
  "is_active": boolean,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Additional Resources

- **[OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)** - Official OpenAI guide
- **[JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)** - Protocol standard
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Python web framework
- **[JWT.io](https://jwt.io/)** - JWT token debugger and validator
- **[Timezone MCP Server](timezone-mcp-server/README.md)** - Reference implementation

## Support & Troubleshooting

For MCP integration questions and issues:

1. **Review Documentation**:
   - [Main README](README.md) - Project overview
   - [MCP Quickstart Guide](docs/MCP_QUICKSTART.md) - Getting started
   - [Timezone MCP Server README](timezone-mcp-server/README.md) - Example implementation

2. **Check Logs**:
   ```bash
   # Chat service logs (MCP integration)
   docker logs chat-service --tail 100
   
   # Your MCP server logs
   docker logs my-mcp-server --tail 100
   
   # All services
   docker-compose logs --tail 50
   ```

3. **Common Issues**:
   - Server URL using `localhost` instead of service name
   - AUTH_SECRET_KEY mismatch between services
   - Server not marked as active in UI
   - Token not being passed in WebSocket connection
   - MCP server not implementing required methods

4. **Open a GitHub Issue** with:
   - MCP server URL and configuration
   - Complete tool schema (from `tools/list`)
   - Relevant logs from `docker logs chat-service`
   - Steps to reproduce the issue
   - Expected vs actual behavior

**GitHub Issues**: https://github.com/vcse59/ConvoAI/issues
