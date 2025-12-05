# pylint: disable=logging-fstring-interpolation,broad-exception-caught
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import json
import logging
from sqlalchemy.orm import Session
from engine.database import get_database
from engine import schemas
from engine import user_crud
from services.openai_service import get_openai_service
from utilities.logging_utils import log_websocket_event
from utilities.response_utils import create_websocket_response
from utilities.validation_utils import validate_message_content
from utilities.datetime_utils import format_timestamp
from middleware.analytics_middleware import track_conversation, track_message, sync_user_profile
import asyncio
import os

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}
        self.conversation_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        log_websocket_event(logger, "connection_established", user_id=user_id)
        logger.info(f"WebSocket connection established for user {user_id} (total: {len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None):
        self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from conversation connections
        for conv_id, connections in self.conversation_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                break
        
        log_websocket_event(logger, "connection_closed", user_id=user_id)
        logger.info(f"WebSocket connection closed for user {user_id} (remaining: {len(self.active_connections)})")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_user(self, message: str, user_id: str):
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)

    async def send_to_conversation(self, message: str, conversation_id: str):
        if conversation_id in self.conversation_connections:
            for connection in self.conversation_connections[conversation_id]:
                await connection.send_text(message)

    def add_to_conversation(self, websocket: WebSocket, conversation_id: str):
        if conversation_id not in self.conversation_connections:
            self.conversation_connections[conversation_id] = []
        self.conversation_connections[conversation_id].append(websocket)

manager = ConnectionManager()

class WebSocketHandler:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")

    async def handle_connection(self, websocket: WebSocket, user_id: Optional[str] = None, token: Optional[str] = None):
        # Store token in websocket state for later use
        websocket.state.user_token = token
        await manager.connect(websocket, user_id)
        
        # Get database session
        db = next(get_database())
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process message based on type
                response = await self.process_message(db, message_data, websocket, user_id)
                
                # Send response back to client
                await manager.send_personal_message(
                    json.dumps(response.model_dump()), 
                    websocket
                )
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
        except json.JSONDecodeError:
            error_response = schemas.WebSocketResponse(
                type="error",
                success=False,
                error="Invalid JSON format"
            )
            await manager.send_personal_message(
                json.dumps(error_response.model_dump()),
                websocket
            )
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            error_response = schemas.WebSocketResponse(
                type="error",
                success=False,
                error=str(e)
            )
            await manager.send_personal_message(
                json.dumps(error_response.model_dump()),
                websocket
            )
        finally:
            db.close()

    async def process_message(
        self, 
        db: Session, 
        message_data: dict, 
        websocket: WebSocket, 
        user_id: Optional[str] = None
    ) -> schemas.WebSocketResponse:
        """Process incoming WebSocket message"""
        
        try:
            message_type = message_data.get("type")
            data = message_data.get("data", {})
            
            if message_type == "start_conversation":
                return await self.handle_start_conversation(db, data, websocket, user_id)
            
            elif message_type == "send_message":
                return await self.handle_send_message(db, data, websocket, user_id)
            
            elif message_type == "end_conversation":
                return await self.handle_end_conversation(db, data, websocket, user_id)
            
            else:
                return schemas.WebSocketResponse(
                    type="error",
                    success=False,
                    error=f"Unknown message type: {message_type}"
                )
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return schemas.WebSocketResponse(
                type="error",
                success=False,
                error=str(e)
            )

    async def handle_start_conversation(
        self, 
        db: Session, 
        data: dict, 
        websocket: WebSocket, 
        user_id: Optional[str] = None
    ) -> schemas.WebSocketResponse:
        """Handle start conversation request"""
        
        try:
            if not self.openai_api_key:
                return schemas.WebSocketResponse(
                    type="start_conversation",
                    success=False,
                    error="OpenAI API key not configured"
                )
            
            openai_service = get_openai_service(self.openai_api_key)
            
            # Parse request data
            request = schemas.StartConversationRequest(**data)
            
            # Start conversation
            conversation = await openai_service.start_conversation(
                db=db,
                user_id=user_id or request.user_id,
                title=request.title,
                system_message=request.system_message
            )
            
            # Log conversation start
            log_websocket_event(
                logger, 
                "conversation_started", 
                user_id=user_id or request.user_id,
                conversation_id=conversation.id
            )
            
            # Add websocket to conversation
            manager.add_to_conversation(websocket, conversation.id)
            
            # Track conversation creation in analytics
            asyncio.create_task(track_conversation(
                conversation_id=str(conversation.id),
                user_id=str(user_id or request.user_id),
                action="created"
            ))
            
            return schemas.WebSocketResponse(
                type="start_conversation",
                success=True,
                data={
                    "conversation_id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return schemas.WebSocketResponse(
                type="start_conversation",
                success=False,
                error=str(e)
            )

    async def handle_send_message(
        self, 
        db: Session, 
        data: dict, 
        websocket: WebSocket, 
        user_id: Optional[str] = None
    ) -> schemas.WebSocketResponse:
        """Handle send message request"""
        
        try:
            if not self.openai_api_key:
                return schemas.WebSocketResponse(
                    type="send_message",
                    success=False,
                    error="OpenAI API key not configured"
                )
            
            openai_service = get_openai_service(self.openai_api_key)
            
            # Parse request data
            request = schemas.SendMessageRequest(**data)
            
            # Get actual user database ID from username for MCP tools
            actual_user_id = user_id
            logger.info(f"Resolving user_id: {user_id}")
            if user_id:
                # user_id here might be username, get the actual database ID
                user = user_crud.get_user_by_username(db, user_id)
                if user:
                    actual_user_id = str(user.id)
                    logger.info(f"Resolved username '{user_id}' to database ID: {actual_user_id}")
                else:
                    logger.warning(f"Could not find user with username: {user_id}")
            else:
                logger.warning("No user_id provided")
            
            # Get token from websocket state
            user_token = getattr(websocket.state, 'user_token', None)
            logger.info(f"Retrieved user_token from websocket: {'present' if user_token else 'None'}")
            
            # Send message and get AI response
            result = await openai_service.send_message(
                db=db,
                conversation_id=request.conversation_id,
                content=request.content,
                user_id=actual_user_id,  # Pass actual user ID for MCP tool access
                user_token=user_token  # Pass user's OAuth token for MCP authentication
            )
            
            # Log message sent
            log_websocket_event(
                logger,
                "message_sent",
                user_id=user_id,
                conversation_id=request.conversation_id,
                message_type="user_message"
            )
            
            # Broadcast to all connections in this conversation
            response_data = {
                "conversation_id": request.conversation_id,
                "user_message": {
                    "id": result["user_message"].id,
                    "content": result["user_message"].content,
                    "timestamp": result["user_message"].timestamp.isoformat()
                },
                "ai_response": {
                    "id": result["ai_response"].id,
                    "content": result["ai_response"].content,
                    "timestamp": result["ai_response"].timestamp.isoformat(),
                    "tokens_used": result["ai_response"].tokens_used
                }
            }
            
            # Only track assistant messages (actual OpenAI interactions) in analytics
            # User messages don't involve OpenAI API calls or token usage
            if user_id:
                # Convert response_time from milliseconds to seconds for analytics
                response_time_seconds = result.get("response_time_ms", 0) / 1000.0 if result.get("response_time_ms") else None
                
                asyncio.create_task(track_message(
                    message_id=str(result["ai_response"].id),
                    conversation_id=str(request.conversation_id),
                    user_id=str(user_id),
                    role="assistant",
                    token_count=result["ai_response"].tokens_used or 0,
                    response_time=response_time_seconds,
                    model_used=result["ai_response"].model
                ))
            
            # Broadcast to conversation participants
            await manager.send_to_conversation(
                json.dumps({
                    "type": "message_broadcast",
                    "data": response_data
                }),
                request.conversation_id
            )
            
            return schemas.WebSocketResponse(
                type="send_message",
                success=True,
                data=response_data
            )
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return schemas.WebSocketResponse(
                type="send_message",
                success=False,
                error=str(e)
            )

    async def handle_end_conversation(
        self, 
        db: Session, 
        data: dict, 
        websocket: WebSocket, 
        user_id: Optional[str] = None
    ) -> schemas.WebSocketResponse:
        """Handle end conversation request"""
        
        try:
            if not self.openai_api_key:
                return schemas.WebSocketResponse(
                    type="end_conversation",
                    success=False,
                    error="OpenAI API key not configured"
                )
            
            openai_service = get_openai_service(self.openai_api_key)
            
            # Parse request data
            request = schemas.EndConversationRequest(**data)
            
            # End conversation
            conversation = await openai_service.end_conversation(
                db=db,
                conversation_id=request.conversation_id
            )
            
            # Log conversation end
            log_websocket_event(
                logger,
                "conversation_ended",
                user_id=user_id,
                conversation_id=request.conversation_id
            )
            
            # Track conversation end in analytics  
            if user_id:
                asyncio.create_task(track_conversation(
                    conversation_id=str(request.conversation_id),
                    user_id=str(user_id),
                    action="ended"
                ))
            
            # Notify all participants
            await manager.send_to_conversation(
                json.dumps({
                    "type": "conversation_ended",
                    "data": {
                        "conversation_id": conversation.id,
                        "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None
                    }
                }),
                request.conversation_id
            )
            
            return schemas.WebSocketResponse(
                type="end_conversation",
                success=True,
                data={
                    "conversation_id": conversation.id,
                    "status": conversation.status,
                    "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            return schemas.WebSocketResponse(
                type="end_conversation",
                success=False,
                error=str(e)
            )

# Create handler instance
websocket_handler = WebSocketHandler()