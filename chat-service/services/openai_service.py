import openai
from openai import AsyncOpenAI
from typing import List, Optional, Dict, Any, Sequence
from sqlalchemy.orm import Session
from engine import models, schemas, crud
from engine.database import get_database
from utilities.logging_utils import log_openai_api_call, setup_logger
from utilities.datetime_utils import get_utc_now
import logging

logger = setup_logger(__name__)

class OpenAIConversationService:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI conversation service
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-3.5-turbo)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.default_system_message = "You are a helpful AI assistant."
    
    async def start_conversation(
        self, 
        db: Session, 
        user_id: Optional[str] = None,  # Changed from int to str for hash-based IDs
        title: Optional[str] = None,
        system_message: Optional[str] = None
    ) -> schemas.ConversationResponse:
        """
        Start a new conversation
        
        Args:
            db: Database session
            user_id: Optional user ID
            title: Optional conversation title
            system_message: Optional system message to set context
            
        Returns:
            ConversationResponse: Created conversation
        """
        try:
            # Create conversation
            conversation_data = schemas.ConversationCreate(
                user_id=user_id,
                title=title or "New Conversation",
                metadata={"model": self.model}
            )
            
            conversation = crud.create_conversation(db, conversation=conversation_data)
            
            # Add system message if provided
            if system_message:
                system_msg = schemas.ChatMessageCreate(
                    conversation_id=conversation.id,
                    role=schemas.MessageRole.SYSTEM,
                    content=system_message or self.default_system_message,
                    model=self.model
                )
                crud.create_message(db, message=system_msg)
            
            logger.info(f"Started conversation {conversation.id} for user {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            raise
    
    async def send_message(
        self,
        db: Session,
        conversation_id: str,  # Changed from int to str for hash-based IDs
        content: str,
        role: schemas.MessageRole = schemas.MessageRole.USER,
        user_id: Optional[str] = None,  # Added for MCP tool access
        user_token: Optional[str] = None  # Added for MCP authentication
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response with MCP tool routing
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            content: Message content
            role: Message role (default: USER)
            user_id: User ID for MCP tool access
            user_token: OAuth token for MCP server authentication
            
        Returns:
            Dict containing user message and AI response
        """
        try:
            # Verify conversation exists and is active
            conversation = crud.get_conversation(db, conversation_id=conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
            
            if conversation.status != "active":
                raise ValueError("Conversation is not active")
            
            # Record start time for response time tracking
            start_time = get_utc_now()
            
            # Save user message
            user_message = schemas.ChatMessageCreate(
                conversation_id=conversation_id,
                role=role,
                content=content,
                model=self.model
            )
            saved_user_message = crud.create_message(db, message=user_message)
            
            # Get conversation history for context
            messages = crud.get_conversation_messages(db, conversation_id=conversation_id)
            
            # Prepare messages for OpenAI API
            openai_messages = []
            for msg in messages:
                # Role is already a string in the database, handle both enum and string
                role_str = msg.role.value if hasattr(msg.role, 'value') else msg.role
                openai_messages.append({
                    "role": role_str,
                    "content": msg.content
                })
            
            # --- MCP Tool Integration ---
            response_content = None
            response_metadata = {}
            tokens_used = None
            
            logger.info(f"send_message called with user_id={user_id}, user_token={'present' if user_token else 'None'}")
            
            if user_id:
                # Try to use MCP tools if available
                from .mcp_tools_service import MCPToolsService
                
                logger.info(f"Creating MCPToolsService with user_token={'present' if user_token else 'None'}")
                mcp_service = MCPToolsService(db, user_id, user_token)
                try:
                    # Discover available MCP tools
                    available_tools = await mcp_service.get_available_tools()
                    
                    if available_tools:
                        # Convert MCP tools to OpenAI function format
                        openai_functions = []
                        tool_map = {}  # Map function names to (server_id, tool_name)
                        
                        for server_data in available_tools:
                            server_id = server_data["server_id"]
                            server_tools = server_data["tools"]
                            
                            for tool in server_tools:
                                tool_name = tool.get("name")
                                function_def = {
                                    "name": tool_name,
                                    "description": tool.get("description", ""),
                                    "parameters": {
                                        "type": "object",
                                        "properties": tool.get("parameters", {}),
                                        "required": []
                                    }
                                }
                                openai_functions.append(function_def)
                                tool_map[tool_name] = (server_id, tool_name)
                        
                        # Call OpenAI with function calling
                        try:
                            response = await self._call_openai_api(
                                openai_messages, 
                                functions=openai_functions
                            )
                            
                            # Check if OpenAI wants to call a function
                            if response.get("function_call"):
                                function_name = response["function_call"]["name"]
                                function_args_str = response["function_call"]["arguments"]
                                
                                import json
                                function_args = json.loads(function_args_str)
                                
                                server_id, tool_name = tool_map[function_name]
                                
                                logger.info(f"OpenAI requested MCP tool: {tool_name} with args: {function_args}")
                                
                                # Call the MCP tool
                                tool_result = await mcp_service.call_tool(
                                    server_id,
                                    tool_name,
                                    function_args
                                )
                                
                                # Format the tool result as response
                                if "error" in tool_result:
                                    response_content = f"I tried to get that information but encountered an error: {tool_result['error']}"
                                else:
                                    # Let the LLM format the tool result
                                    result_str = json.dumps(tool_result.get("result", tool_result))
                                    
                                    # Add function result to messages and get final response
                                    messages_with_result = openai_messages + [
                                        {"role": "assistant", "content": None, "function_call": response["function_call"]},
                                        {"role": "function", "name": function_name, "content": result_str}
                                    ]
                                    
                                    final_response = await self._call_openai_api(messages_with_result)
                                    response_content = final_response["content"]
                                    tokens_used = response.get("tokens_used", 0) + final_response.get("tokens_used", 0)
                                    
                                response_metadata = {
                                    "mcp_tool_used": True,
                                    "tool_name": tool_name,
                                    "server_id": server_id,
                                    "tool_result": tool_result
                                }
                            else:
                                # OpenAI responded directly without using tools
                                response_content = response["content"]
                                tokens_used = response.get("tokens_used")
                                response_metadata = {"mcp_tool_used": False}
                        except Exception as e:
                            logger.error(f"Error in MCP function calling: {e}")
                            # Fall back to normal response
                            response_content = None
                    
                finally:
                    await mcp_service.close()
            
            # If no MCP response generated, fall back to standard OpenAI call
            if response_content is None:
                response = await self._call_openai_api(openai_messages)
                response_content = response["content"]
                tokens_used = response.get("tokens_used")
                response_metadata.update(response.get("metadata", {}))
            
            # Calculate total response time
            end_time = get_utc_now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Save AI response with response time
            ai_message = schemas.ChatMessageCreate(
                conversation_id=conversation_id,
                role=schemas.MessageRole.ASSISTANT,
                content=response_content,
                model=self.model,
                tokens_used=tokens_used,
                response_time=response_time_ms,
                metadata=response_metadata
            )
            saved_ai_message = crud.create_message(db, message=ai_message)
            
            logger.info(f"Processed message in conversation {conversation_id}")
            
            return {
                "user_message": saved_user_message,
                "ai_response": saved_ai_message,
                "conversation_id": conversation_id,
                "response_time_ms": response_time_ms
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
    
    async def end_conversation(
        self,
        db: Session,
        conversation_id: str  # Changed from int to str for hash-based IDs
    ) -> schemas.ConversationResponse:
        """
        End a conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            ConversationResponse: Updated conversation
        """
        try:
            conversation = crud.end_conversation(db, conversation_id=conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
            
            logger.info(f"Ended conversation {conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            raise
    
    async def get_conversation_context(
        self,
        db: Session,
        conversation_id: str,  # Changed from int to str for hash-based IDs
        limit: int = 10
    ) -> Sequence[schemas.ChatMessageResponse]:  # Changed to Sequence for covariance
        """
        Get recent messages from a conversation for context
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Number of recent messages to retrieve
            
        Returns:
            Sequence of recent messages
        """
        try:
            messages = crud.get_conversation_messages(
                db, 
                conversation_id=conversation_id, 
                limit=limit
            )
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            raise
    
    async def _call_openai_api(self, messages: List[Dict[str, str]], functions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Call OpenAI API with error handling and token tracking
        
        Args:
            messages: List of messages for OpenAI API
            functions: Optional list of function definitions for OpenAI function calling
            
        Returns:
            Dict containing response content and metadata
        """
        try:
            # Record start time for performance logging
            start_time = get_utc_now()
            
            # Prepare API call parameters
            api_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Add functions if provided
            if functions:
                api_params["functions"] = functions
                api_params["function_call"] = "auto"
            
            # Use the new OpenAI v1.x API
            response = await self.client.chat.completions.create(**api_params)
            
            # Calculate response time
            end_time = get_utc_now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "tokens_used": response.usage.total_tokens,
                "metadata": {
                    "model": self.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
            
            # Include function_call if present
            if hasattr(message, 'function_call') and message.function_call:
                result["function_call"] = {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            
            # Log successful API call
            log_openai_api_call(
                logger,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                response_time_ms=response_time_ms,
                success=True
            )
            
            return result
            
        except openai.RateLimitError as e:
            error_msg = "API rate limit exceeded. Please try again later."
            log_openai_api_call(logger, model=self.model, success=False, error=error_msg)
            raise ValueError(error_msg)
        
        except openai.BadRequestError as e:
            error_msg = "Invalid request to OpenAI API"
            log_openai_api_call(logger, model=self.model, success=False, error=str(e))
            raise ValueError(error_msg)
        
        except openai.AuthenticationError as e:
            error_msg = "OpenAI API authentication failed"
            log_openai_api_call(logger, model=self.model, success=False, error=str(e))
            raise ValueError(error_msg)
        
        except Exception as e:
            error_msg = f"OpenAI API error: {str(e)}"
            log_openai_api_call(logger, model=self.model, success=False, error=str(e))
            raise ValueError(error_msg)

# Singleton instance
_openai_service = None

def get_openai_service(api_key: str) -> OpenAIConversationService:
    """
    Get or create OpenAI service instance
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        OpenAIConversationService instance
    """
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIConversationService(api_key)
    return _openai_service