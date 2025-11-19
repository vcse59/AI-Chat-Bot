# MCP Server Integration Guide

## Overview

The AI ChatBot Platform supports **Model Context Protocol (MCP) server integration**, allowing users to register custom MCP servers and extend the AI's capabilities with external tools.

## Features

- ✅ **User-Friendly UI**: Register MCP servers through the web interface
- ✅ **Automatic Authentication**: User tokens are automatically passed to MCP servers
- ✅ **Tool Discovery**: Automatic discovery of tools from registered servers
- ✅ **OpenAI Integration**: Tools are seamlessly passed to OpenAI using function calling
- ✅ **Per-User Configuration**: Each user manages their own MCP servers
- ✅ **Active/Inactive Toggle**: Enable or disable servers without deleting them

## How It Works

### Architecture

```
User ─┬─► Web UI (MCP Server Manager)
      │     └─► Register MCP Server (Name, URL)
      │
      └─► Chat Interface
            └─► Send Message ──► Chat Service
                                   ├─► Discover Tools from Active MCP Servers
                                   ├─► Convert Tools to OpenAI Functions
                                   ├─► Call OpenAI with Functions
                                   └─► If function_call returned:
                                         ├─► Execute MCP Tool (with user token)
                                         └─► Return result to OpenAI
```

### Authentication Flow

1. User logs in → Receives JWT token
2. Token stored in browser's localStorage
3. User registers MCP server (no auth credentials needed)
4. When chatting:
   - User token automatically included in WebSocket connection
   - Token passed to `mcp_tools_service`
   - Token sent as `Authorization: Bearer <token>` to MCP servers
5. MCP servers validate the token and execute tools

## Registering an MCP Server

### Via Web Interface

1. **Log in** to the platform (http://localhost:3000)

2. **Click the "🔌 MCP Servers" button** in the top navigation bar

3. **Click "+ Add MCP Server"**

4. **Fill in the form**:
   - **Name**: Descriptive name (e.g., "Timezone Server")
   - **Description**: Optional description of what the server does
   - **Server URL**: The MCP server endpoint
     - For local Docker services: `http://service-name:port/mcp`
     - Example: `http://timezone-mcp-server:8003/mcp`
   - **Active**: Check to enable immediately

5. **Click "Create Server"**

### Example: Timezone MCP Server

The platform includes a built-in timezone MCP server as an example.

**Register it with**:
- **Name**: "Timezone Server"
- **Description**: "Get current time in any timezone"
- **Server URL**: `http://timezone-mcp-server:8003/mcp`
- **Active**: ✓

**Test it by asking**:
- "What time is it in Tokyo?"
- "Tell me the current time in New York"
- "What's the time in London right now?"

The AI will automatically use the timezone MCP server tool to answer.

## Creating Your Own MCP Server

### MCP Server Requirements

Your MCP server must:
1. Accept JSON-RPC 2.0 requests
2. Implement the `tools/list` method to advertise available tools
3. Implement tool execution via JSON-RPC
4. Accept and validate JWT tokens from the `Authorization` header

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
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

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
    - ai-chatbot-network
```

### Register in UI

After deploying, register your server:
- **Name**: "My Custom Server"
- **Server URL**: `http://my-mcp-server:8003/mcp`

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
   docker logs openai-chatbot-api --tail 50
   ```
   Look for:
   - `Discovered X MCP servers with tools`
   - `OpenAI requested MCP tool: tool_name`
   - `Calling MCP tool: tool_name with args: {...}`

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

**Causes**:
- Server URL is incorrect
- Server is not running
- Server is not accessible from chat-service container
- Firewall blocking connection

**Solutions**:
1. Verify server is running: `docker ps | grep my-server`
2. Check Docker network: `docker network inspect ai-chatbot-network`
3. Use service names not localhost: `http://my-server:port` not `http://localhost:port`
4. Test connectivity: `docker exec openai-chatbot-api curl http://my-server:port/mcp`

### Tools Not Appearing in OpenAI

**Check tool discovery**:
```bash
docker logs openai-chatbot-api --tail 100 | grep "Discovered.*MCP servers"
```

**Should see**:
```
INFO:services.mcp_tools_service:Discovered 1 MCP servers with tools for user xxx
```

**If seeing 0 servers**:
1. User token not being passed (check WebSocket connection includes token)
2. Server URL unreachable
3. Server returning error on `tools/list`
4. Server not marked as active

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
- ✅ Always validate JWT tokens in your MCP server
- ✅ Use the same `AUTH_SECRET_KEY` as the platform
- ✅ Implement rate limiting for tool calls
- ✅ Sanitize and validate all input parameters
- ✅ Log all tool executions for audit trails

### Performance
- ✅ Keep tool execution fast (<5 seconds)
- ✅ Return errors quickly if tool can't execute
- ✅ Implement caching for expensive operations
- ✅ Use async/await for I/O operations

### Usability
- ✅ Write clear, descriptive tool names
- ✅ Provide detailed parameter descriptions
- ✅ Include examples in descriptions
- ✅ Return user-friendly error messages
- ✅ Test with various input combinations

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

**Service**: `chat-service/services/mcp_tools_service.py`

**Key Methods**:
- `get_available_tools()` - Discovers tools from all active MCP servers
- `call_tool(server_id, tool_name, arguments)` - Executes a specific tool
- `_discover_server_tools(server)` - Calls `tools/list` on MCP server
- `_call_tool_on_server(server, tool_name, arguments)` - Calls `tools/call`

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

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: All endpoints require `Authorization: Bearer <token>`

#### List MCP Servers
```http
GET /mcp-servers/
Query Params:
  - active_only: boolean (default: false)
  - skip: int (default: 0)
  - limit: int (default: 100)

Response: MCPServerResponse[]
```

#### Create MCP Server
```http
POST /mcp-servers/
Body: {
  "name": "string",
  "description": "string?",
  "server_url": "string",
  "is_active": boolean
}

Response: MCPServerResponse
```

#### Get MCP Server
```http
GET /mcp-servers/{server_id}

Response: MCPServerResponse
```

#### Update MCP Server
```http
PUT /mcp-servers/{server_id}
Body: {
  "name": "string?",
  "description": "string?",
  "server_url": "string?",
  "is_active": boolean?
}

Response: MCPServerResponse
```

#### Delete MCP Server
```http
DELETE /mcp-servers/{server_id}

Response: 200 OK
```

## Additional Resources

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT.io](https://jwt.io/) - JWT token debugger

## Support

For MCP integration questions:
1. Check the [Main README](README.md)
2. Review [MCP Quickstart Guide](docs/MCP_QUICKSTART.md)
3. See [MCP Implementation Summary](docs/MCP_IMPLEMENTATION_SUMMARY.md)
4. Open an issue on GitHub with:
   - MCP server URL
   - Tool schema
   - Logs from `docker logs openai-chatbot-api`
   - Steps to reproduce
