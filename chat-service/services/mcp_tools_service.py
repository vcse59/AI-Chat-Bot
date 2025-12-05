"""
MCP Tools Service - Manages interaction with MCP servers
"""
# pylint: disable=logging-fstring-interpolation,broad-exception-caught
import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from engine import mcp_server_crud

logger = logging.getLogger(__name__)

class MCPToolsService:
    """Service to discover and interact with MCP server tools"""
    
    def __init__(self, db: Session, user_id: str, user_token: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.user_token = user_token
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get all available tools from user's active MCP servers
        
        Returns:
            List of tool definitions with format:
            {
                "server_id": "mcp_xxx",
                "server_name": "Timezone MCP Server",
                "server_url": "http://localhost:8003",
                "tools": [
                    {
                        "name": "get_current_time",
                        "description": "Get current time in timezone",
                        "parameters": {...}
                    }
                ]
            }
        """
        tools = []
        
        try:
            # Get user's active MCP servers
            servers = mcp_server_crud.get_user_mcp_servers(
                self.db, 
                self.user_id, 
                active_only=True
            )
            
            for server in servers:
                try:
                    # Discover tools from each server
                    server_tools = await self._discover_server_tools(server)
                    if server_tools:
                        tools.append({
                            "server_id": server.id,
                            "server_name": server.name,
                            "server_url": server.server_url,
                            "api_key": server.api_key,
                            "tools": server_tools
                        })
                except Exception as e:
                    logger.warning(f"Failed to discover tools from {server.name}: {e}")
                    continue
            
            logger.info(f"Discovered {len(tools)} MCP servers with tools for user {self.user_id}")
            return tools
            
        except Exception as e:
            logger.error(f"Error getting available tools: {e}")
            return []
    
    async def _discover_server_tools(self, server) -> List[Dict[str, Any]]:
        """
        Discover tools from an MCP server using JSON-RPC protocol
        """
        try:
            headers = {"Content-Type": "application/json"}
            # Use user's OAuth token for authentication
            logger.info(f"Calling {server.name}: user_token={'present' if self.user_token else 'None'}, api_key={'present' if server.api_key else 'None'}")
            if self.user_token:
                headers["Authorization"] = f"Bearer {self.user_token}"
                logger.info(f"Using user OAuth token for {server.name}")
            elif server.api_key:
                headers["Authorization"] = f"Bearer {server.api_key}"
                logger.info(f"Using server API key for {server.name}")
            
            # Call tools/list using JSON-RPC 2.0
            json_rpc_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.client.post(
                server.server_url,  # Assumes server_url is the MCP endpoint (e.g., /mcp)
                json=json_rpc_request,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "tools" in result["result"]:
                    # Transform MCP tool format to our internal format
                    tools = []
                    for tool in result["result"]["tools"]:
                        tools.append({
                            "name": tool.get("name"),
                            "description": tool.get("description"),
                            "parameters": tool.get("inputSchema", {}).get("properties", {})
                        })
                    return tools
                else:
                    logger.warning(f"Server {server.name} returned unexpected format: {result}")
                    return []
            else:
                logger.warning(f"Server {server.name} returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error discovering tools from {server.name}: {e}")
            return []
    
    async def call_tool(
        self, 
        server_id: str, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a specific tool on an MCP server using JSON-RPC protocol
        
        Args:
            server_id: MCP server ID
            tool_name: Name of the tool to call
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            # Get server details
            server = mcp_server_crud.get_mcp_server(self.db, server_id)
            if not server:
                return {"error": "MCP server not found"}
            
            if str(server.user_id) != str(self.user_id):
                return {"error": "Access denied to this MCP server"}
            
            if not server.is_active:
                return {"error": "MCP server is not active"}
            
            # Prepare request
            headers = {"Content-Type": "application/json"}
            # Use user's OAuth token for authentication
            if self.user_token:
                headers["Authorization"] = f"Bearer {self.user_token}"
            elif server.api_key:
                headers["Authorization"] = f"Bearer {server.api_key}"
            
            # Call the tool using JSON-RPC 2.0
            json_rpc_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            response = await self.client.post(
                server.server_url,
                json=json_rpc_request,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    # Extract content from MCP response
                    mcp_result = result["result"]
                    if "content" in mcp_result:
                        # Content is an array in MCP protocol
                        content_items = mcp_result["content"]
                        if content_items and len(content_items) > 0:
                            # Return the first content item's text
                            return {"result": content_items[0].get("text", "")}
                        else:
                            return {"result": mcp_result}
                    else:
                        return {"result": mcp_result}
                elif "error" in result:
                    error = result["error"]
                    return {"error": error.get("message", "Unknown error"), "code": error.get("code")}
                else:
                    logger.warning(f"Unexpected response format from {server.name}: {result}")
                    return {"error": "Unexpected response format", "response": result}
            else:
                error_msg = f"Tool execution failed: {response.status_code}"
                logger.error(error_msg)
                return {"error": error_msg, "status_code": response.status_code}
                
        except Exception as e:
            error_msg = f"Error calling tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def format_tools_for_prompt(self, tools_data: List[Dict[str, Any]]) -> str:
        """
        Format discovered tools into a prompt-friendly string
        
        Returns:
            Formatted string describing available tools
        """
        if not tools_data:
            return "No MCP tools are currently available."
        
        prompt_parts = ["You have access to the following MCP tools:\n"]
        
        for server_data in tools_data:
            server_name = server_data["server_name"]
            server_tools = server_data["tools"]
            
            if not server_tools:
                continue
                
            prompt_parts.append(f"\n**{server_name}:**")
            
            for tool in server_tools:
                tool_name = tool.get("name", "unknown")
                tool_desc = tool.get("description", "No description")
                tool_params = tool.get("parameters", {})
                
                prompt_parts.append(f"  - {tool_name}: {tool_desc}")
                
                if tool_params:
                    params_str = ", ".join([
                        f"{k} ({v.get('type', 'any')})" 
                        for k, v in tool_params.items()
                    ])
                    prompt_parts.append(f"    Parameters: {params_str}")
        
        prompt_parts.append("\n\nTo use a tool, respond with a JSON object in this format:")
        prompt_parts.append('{"use_tool": true, "server_id": "...", "tool_name": "...", "parameters": {...}}')
        prompt_parts.append("\nIf no tool is needed, respond normally to the user's query.")
        
        return "\n".join(prompt_parts)


async def analyze_intent_with_llm(
    openai_service,
    user_query: str,
    tools_context: str,
    conversation_history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Analyze user query intent using LLM with MCP tools context
    
    Args:
        openai_service: OpenAI service instance
        user_query: User's query
        tools_context: Formatted tools description
        conversation_history: Previous messages for context
        
    Returns:
        Dict with intent analysis and tool call decision
    """
    # Build the intent analysis prompt
    system_prompt = f"""You are an AI assistant with access to MCP (Model Context Protocol) tools.

{tools_context}

Analyze the user's query and decide if you need to use any MCP tools or if you can answer directly.

If you need to use a tool:
- Respond with a JSON object: {{"use_tool": true, "server_id": "...", "tool_name": "...", "parameters": {{...}}, "explanation": "why this tool is needed"}}

If you can answer directly without tools:
- Respond with a JSON object: {{"use_tool": false, "response": "your direct answer to the user"}}

Be precise and only use tools when truly necessary."""

    # Build conversation context
    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        messages.extend(conversation_history[-5:])  # Last 5 messages for context
    
    messages.append({"role": "user", "content": user_query})
    
    try:
        # Use openai_service's _call_openai_api method for consistent API handling
        response = await openai_service._call_openai_api(messages)
        
        content = response["content"]
        
        # Try to parse as JSON
        import json
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # If not valid JSON, treat as direct response
            return {
                "use_tool": False,
                "response": content
            }
            
    except Exception as e:
        logger.error(f"Error analyzing intent with LLM: {e}")
        return {
            "use_tool": False,
            "response": "I encountered an error analyzing your request. Please try again.",
            "error": str(e)
        }
