"""
Timezone MCP Server with HTTP/SSE Transport
Supports both MCP Inspector (SSE) and REST API for chat-service integration
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional, Dict, List
import os
from contextlib import asynccontextmanager

import httpx
import pytz
from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel
import json
from starlette.responses import Response
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("timezone-mcp-server")

# Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-server:8001")

# Create FastAPI app
app = FastAPI(title="Timezone MCP Server")

# Create MCP server
mcp_server = Server("timezone-mcp-server")


class ToolCallRequest(BaseModel):
    timezone: Optional[str] = None
    filter: Optional[str] = None
    time: Optional[str] = None
    from_timezone: Optional[str] = None
    to_timezone: Optional[str] = None


class TimezoneService:
    """Service for timezone operations"""
    
    @staticmethod
    def get_current_time(timezone_name: str) -> dict:
        """Get current time in specified timezone"""
        try:
            tz = pytz.timezone(timezone_name)
            current_time = datetime.now(tz)
            return {
                "timezone": timezone_name,
                "current_time": current_time.isoformat(),
                "utc_offset": current_time.strftime("%z"),
                "timezone_abbreviation": current_time.tzname(),
                "is_dst": bool(current_time.dst())
            }
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {timezone_name}")
    
    @staticmethod
    def list_timezones(filter_text: Optional[str] = None) -> list:
        """List available timezones, optionally filtered"""
        all_timezones = pytz.all_timezones
        if filter_text:
            return [tz for tz in all_timezones if filter_text.lower() in tz.lower()]
        return list(all_timezones)
    
    @staticmethod
    def convert_time(time_str: str, from_tz: str, to_tz: str) -> dict:
        """Convert time between timezones"""
        try:
            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)
            
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = from_timezone.localize(dt)
            
            converted_dt = dt.astimezone(to_timezone)
            
            return {
                "original_time": time_str,
                "from_timezone": from_tz,
                "to_timezone": to_tz,
                "converted_time": converted_dt.isoformat(),
                "utc_offset": converted_dt.strftime("%z")
            }
        except Exception as e:
            raise ValueError(f"Time conversion failed: {str(e)}")
    
    @staticmethod
    def get_timezone_by_location(location: str) -> str:
        """Get timezone by location (city/country)"""
        location_lower = location.lower()
        
        location_map = {
            "new york": "America/New_York",
            "los angeles": "America/Los_Angeles",
            "chicago": "America/Chicago",
            "london": "Europe/London",
            "paris": "Europe/Paris",
            "tokyo": "Asia/Tokyo",
            "sydney": "Australia/Sydney",
            "mumbai": "Asia/Kolkata",
            "beijing": "Asia/Shanghai",
            "dubai": "Asia/Dubai",
            "singapore": "Asia/Singapore",
            "toronto": "America/Toronto",
            "berlin": "Europe/Berlin",
            "moscow": "Europe/Moscow",
            "san francisco": "America/Los_Angeles",
            "seattle": "America/Los_Angeles",
            "boston": "America/New_York",
            "washington": "America/New_York",
            "miami": "America/New_York",
            "denver": "America/Denver",
            "phoenix": "America/Phoenix",
            "las vegas": "America/Los_Angeles",
        }
        
        for key, tz in location_map.items():
            if key in location_lower:
                return tz
        
        # Try to use the location as-is (might be a valid timezone)
        try:
            pytz.timezone(location)
            return location
        except:
            pass
        
        # Try common typo fixes
        location_fixed = location.replace(" ", "_")
        try:
            pytz.timezone(location_fixed)
            return location_fixed
        except:
            pass
        
        raise ValueError(f"Could not determine timezone for location: {location}. Try using standard timezone format like 'America/New_York'")


timezone_service = TimezoneService()


# ============================================================================
# Helper Functions
# ============================================================================

def serialize_tool(tool: Tool) -> dict:
    """Serialize a Tool object with all required MCP fields"""
    tool_dict = tool.model_dump()
    
    # Ensure all required fields are present (MCP Inspector validation)
    if "title" not in tool_dict or tool_dict["title"] is None:
        tool_dict["title"] = tool_dict["name"]
    if "outputSchema" not in tool_dict or tool_dict["outputSchema"] is None:
        tool_dict["outputSchema"] = {"type": "object"}
    if "annotations" not in tool_dict or tool_dict["annotations"] is None:
        tool_dict["annotations"] = {}
    if "icons" not in tool_dict or tool_dict["icons"] is None:
        tool_dict["icons"] = []
    
    return tool_dict


# ============================================================================
# MCP Protocol Handlers (for MCP Inspector)
# ============================================================================

@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="get_current_time",
            description="Get current time in a timezone",
            inputSchema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone name (e.g., 'America/New_York') or location (e.g., 'New York')"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_timezones",
            description="List all available timezones, optionally filtered",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": "Filter timezones by text (optional)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="convert_time",
            description="Convert time between timezones",
            inputSchema={
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "Time to convert (ISO format)"
                    },
                    "from_timezone": {
                        "type": "string",
                        "description": "Source timezone"
                    },
                    "to_timezone": {
                        "type": "string",
                        "description": "Target timezone"
                    }
                },
                "required": ["time", "from_timezone", "to_timezone"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle MCP tool calls"""
    try:
        if name == "get_current_time":
            timezone = arguments.get("timezone", "UTC")
            if "/" not in timezone:
                timezone = timezone_service.get_timezone_by_location(timezone)
            result = timezone_service.get_current_time(timezone)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_timezones":
            filter_text = arguments.get("filter")
            timezones = timezone_service.list_timezones(filter_text)
            result = {"total": len(timezones), "timezones": timezones[:50]}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "convert_time":
            result = timezone_service.convert_time(
                arguments["time"],
                arguments["from_timezone"],
                arguments["to_timezone"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ============================================================================
# HTTP/SSE Endpoints (for MCP Inspector)
# ============================================================================

# Store active MCP sessions
mcp_sessions: Dict[str, Dict[str, Any]] = {}

async def verify_mcp_auth(request: Request) -> Optional[Dict[str, Any]]:
    """Verify authentication for MCP endpoints"""
    # Check Authorization header
    authorization = request.headers.get("authorization") or request.headers.get("Authorization")
    
    if not authorization:
        logger.warning("No authorization header provided")
        return None
    
    if not authorization.startswith("Bearer "):
        logger.warning(f"Invalid authorization format: {authorization[:20]}")
        return None
    
    token = authorization.split(" ")[1]
    
    # Verify token with auth-service
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            user_info = response.json()
            logger.info(f"Authenticated user: {user_info.get('username')}")
            return user_info
        except httpx.HTTPStatusError as e:
            logger.error(f"Token verification failed: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Auth service error: {e}")
            return None


@app.get("/sse")
async def handle_sse(request: Request):
    """SSE endpoint for MCP Inspector - Server-Sent Events transport"""
    
    # Verify authentication
    user_info = await verify_mcp_auth(request)
    if not user_info:
        return Response(
            content=json.dumps({"error": "Unauthorized", "message": "Valid Bearer token required"}),
            status_code=401,
            media_type="application/json",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    session_id = request.headers.get("x-session-id", f"session_{id(request)}")
    logger.info(f"SSE connection established for session: {session_id}, user: {user_info.get('username')}")
    
    from anyio import create_memory_object_stream
    import anyio
    
    # Create bidirectional streams for MCP communication
    read_stream_send, read_stream_receive = create_memory_object_stream(100)
    write_stream_send, write_stream_receive = create_memory_object_stream(100)
    
    # Store session
    mcp_sessions[session_id] = {
        "read_send": read_stream_send,
        "write_receive": write_stream_receive
    }
    
    async def sse_event_generator():
        """Generate SSE events from MCP server"""
        try:
            # Run MCP server in background
            async def run_mcp():
                try:
                    await mcp_server.run(
                        read_stream_receive,
                        write_stream_send,
                        mcp_server.create_initialization_options()
                    )
                except Exception as e:
                    logger.error(f"MCP server error: {e}", exc_info=True)
            
            # Start MCP server task
            async with anyio.create_task_group() as tg:
                tg.start_soon(run_mcp)
                
                # Send endpoint info
                yield f"event: endpoint\ndata: /messages\n\n"
                
                # Stream messages from write_stream to SSE
                async for message in write_stream_receive:
                    if isinstance(message, bytes):
                        message_str = message.decode('utf-8')
                    else:
                        message_str = json.dumps(message) if not isinstance(message, str) else message
                    
                    # Send as SSE message event
                    yield f"event: message\ndata: {message_str}\n\n"
                    
        except Exception as e:
            logger.error(f"SSE streaming error: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': 'Internal server error'})}\n\n"
        finally:
            # Cleanup session
            if session_id in mcp_sessions:
                del mcp_sessions[session_id]
    
    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/mcp")
async def handle_mcp_post(request: Request):
    """MCP endpoint for direct JSON-RPC communication (alternative to SSE)"""
    
    # Parse the message first to get the ID for proper error response
    try:
        message = await request.json()
        msg_id = message.get("id")
    except Exception as e:
        logger.error(f"Failed to parse MCP POST body: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error: invalid JSON"}
        }
    
    # Verify authentication
    user_info = await verify_mcp_auth(request)
    if not user_info:
        return Response(
            content=json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32001,
                    "message": "Unauthorized: Valid Bearer token required"
                }
            }),
            status_code=401,
            media_type="application/json",
            headers={"WWW-Authenticate": "Bearer realm=\"MCP Server\""}
        )
    
    try:
        logger.info(f"MCP POST request from {user_info.get('username')}: {message}")
        
        method = message.get("method")
        params = message.get("params", {})
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "timezone-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "notifications/initialized":
            return {"jsonrpc": "2.0", "result": {}}
        elif method == "tools/list":
            tools = await list_tools()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": [serialize_tool(t) for t in tools]}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = await call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [c.model_dump() for c in result]}
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
    except Exception as e:
        logger.error(f"Error handling MCP POST: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal server error"}
        }


@app.get("/mcp")
async def handle_mcp_get(request: Request):
    """MCP endpoint info (GET)"""
    return {
        "name": "timezone-mcp-server",
        "version": "1.0.0",
        "description": "Timezone MCP Server with HTTP/SSE support",
        "authentication": {
            "type": "bearer",
            "description": "Requires Bearer token from auth-service",
            "header": "Authorization: Bearer <token>"
        },
        "transports": [
            {"type": "sse", "url": "/sse"},
            {"type": "http", "url": "/mcp"}
        ],
        "capabilities": ["tools"]
    }


@app.post("/messages")
async def handle_messages(request: Request):
    """Handle MCP protocol messages via POST (for SSE transport)"""
    
    # Parse the message first
    try:
        message = await request.json()
        msg_id = message.get("id")
    except Exception as e:
        logger.error(f"JSON parse error: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"}
        }
    
    # Verify authentication
    user_info = await verify_mcp_auth(request)
    if not user_info:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32001,
                "message": "Unauthorized: Valid Bearer token required"
            }
        }
    
    session_id = request.headers.get("x-session-id")
    
    try:
        logger.info(f"Received message from {user_info.get('username')} for session {session_id}: {message}")
        
        # If we have an active session, send through the stream
        if session_id and session_id in mcp_sessions:
            read_send = mcp_sessions[session_id]["read_send"]
            await read_send.send(message)
            return {"status": "queued"}
        
        # Otherwise, handle directly
        method = message.get("method")
        params = message.get("params", {})
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "timezone-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "notifications/initialized":
            return {"jsonrpc": "2.0", "result": {}}
        elif method == "tools/list":
            tools = await list_tools()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": [serialize_tool(t) for t in tools]}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = await call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [c.model_dump() for c in result]}
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal server error"}
        }


# ============================================================================
# REST API Endpoints (for chat-service integration)
# ============================================================================

async def verify_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Verify OAuth token with auth-service"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(status_code=500, detail="Authentication service error")


@app.get("/tools")
async def list_tools_rest():
    """REST endpoint to list available tools"""
    tools = [
        {
            "name": "get_current_time",
            "description": "Get current time in a timezone",
            "parameters": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone name (e.g., 'America/New_York') or location (e.g., 'New York')"
                }
            }
        },
        {
            "name": "list_timezones",
            "description": "List all available timezones, optionally filtered",
            "parameters": {
                "filter": {
                    "type": "string",
                    "description": "Filter timezones by text (optional)"
                }
            }
        },
        {
            "name": "convert_time",
            "description": "Convert time between timezones",
            "parameters": {
                "time": {
                    "type": "string",
                    "description": "Time to convert (ISO format)"
                },
                "from_timezone": {
                    "type": "string",
                    "description": "Source timezone"
                },
                "to_timezone": {
                    "type": "string",
                    "description": "Target timezone"
                }
            }
        }
    ]
    return {"tools": tools}


@app.post("/tools/get_current_time")
async def get_current_time_rest(
    request: ToolCallRequest,
    user_info: Dict = Header(None, alias="Authorization")
):
    """REST endpoint to get current time"""
    try:
        timezone = request.timezone or "UTC"
        if "/" not in timezone:
            timezone = timezone_service.get_timezone_by_location(timezone)
        
        result = timezone_service.get_current_time(timezone)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error getting current time: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/list_timezones")
async def list_timezones_rest(
    request: ToolCallRequest,
    user_info: Dict = Header(None, alias="Authorization")
):
    """REST endpoint to list timezones"""
    try:
        timezones = timezone_service.list_timezones(request.filter)
        return {
            "success": True,
            "result": {
                "total": len(timezones),
                "timezones": timezones[:100],
                "truncated": len(timezones) > 100
            }
        }
    except Exception as e:
        logger.error(f"Error listing timezones: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/convert_time")
async def convert_time_rest(
    request: ToolCallRequest,
    user_info: Dict = Header(None, alias="Authorization")
):
    """REST endpoint to convert time"""
    try:
        if not request.time or not request.from_timezone or not request.to_timezone:
            raise ValueError("time, from_timezone, and to_timezone are required")
        
        result = timezone_service.convert_time(
            request.time,
            request.from_timezone,
            request.to_timezone
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error converting time: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "timezone-mcp-server"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
