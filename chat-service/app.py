# pylint: disable=logging-fstring-interpolation,broad-exception-caught
# Load environment variables FIRST before any local imports
from dotenv import load_dotenv
from pathlib import Path

# Load root .env first (shared config)
root_env = Path(__file__).parent.parent / ".env"
load_dotenv(root_env)

# Load local .env for service-specific overrides
load_dotenv()

from fastapi import FastAPI, WebSocket, Query, WebSocketException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
from typing import Optional

# Use absolute imports for Docker compatibility
from engine.database import engine, Base
from api.routes import router as api_router
from websocket.chat_handler import websocket_handler
from security.oauth import verify_token
from middleware.analytics_middleware import AnalyticsMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ConvoAI API with WebSocket Chat",
    description="A user-centric conversation API with real-time chat via WebSocket",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Analytics middleware
app.add_middleware(AnalyticsMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to ConvoAI API",
        "version": "2.0.0",
        "features": [
            "User management and authentication",
            "User-scoped conversation management",
            "Real-time chat via WebSocket",
            "OpenAI integration for AI conversations",
            "Conversation reconnection and context management"
        ],
        "endpoints": {
            "docs": "/docs",
            "api": "/api/v1/",
            "websocket_chat": "/ws/chat/{user_id}",
            "websocket_anonymous": "/ws/chat"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

# WebSocket endpoints
@app.websocket("/ws/{conversation_id}")
async def websocket_conversation(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for conversation-specific connections
    Requires JWT token as query parameter: ws://host/ws/{conversation_id}?token=YOUR_JWT_TOKEN
    
    This endpoint is used by the frontend to connect to a specific conversation
    """
    # Verify token is provided
    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication token required"
        )
    
    try:
        # Verify the JWT token
        payload = verify_token(token)
        username = payload.get("sub")
        
        if not username:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid token: missing username"
            )
        
        # Verify the user has access to this conversation
        from engine.database import get_database
        from engine import conversation_crud
        
        db = next(get_database())
        try:
            conversation = conversation_crud.get_conversation(db, conversation_id)
            if not conversation:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA,
                    reason="Conversation not found"
                )
            
            # Get user by username to get the user_id
            from engine import user_crud
            user = user_crud.get_user_by_username(db, username)
            if not user:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="User not found"
                )
            
            # Verify conversation belongs to this user (handle type mismatch)
            if str(conversation.user_id) != str(user.id):
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Access denied: conversation does not belong to this user"
                )
            
            # Connect the WebSocket
            await websocket_handler.handle_connection(websocket, user.id)
            
        finally:
            db.close()
            
    except WebSocketException:
        raise
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {str(e)}")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Authentication failed: {str(e)}"
        )

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat_with_user(
    websocket: WebSocket, 
    user_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for authenticated users
    Requires JWT token as query parameter: ws://host/ws/chat/{user_id}?token=YOUR_JWT_TOKEN
    
    Supports:
    1. Start Conversation
    2. Send Message 
    3. End Conversation
    4. Real-time AI responses
    """
    # Verify token if provided
    if token:
        try:
            payload = verify_token(token)
            token_user_id = payload.get("sub")
            
            # Verify the token user_id matches the path user_id
            if token_user_id != user_id:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Token user_id does not match path user_id"
                )
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {str(e)}")
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid or expired token"
            )
    else:
        # Allow connection without token but log it
        logger.warning(f"WebSocket connection for user {user_id} without authentication token")
    
    await websocket_handler.handle_connection(websocket, user_id, token)

@app.websocket("/ws/chat")
async def websocket_chat_anonymous(websocket: WebSocket):
    """
    WebSocket endpoint for anonymous users (no authentication required)
    Supports the same operations as authenticated endpoint
    """
    await websocket_handler.handle_connection(websocket)

# Additional endpoints for chat management
@app.get("/api/v1/chat/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: int):
    """Export conversation as JSON"""
    # This would be implemented to export conversation history
    return {"message": f"Export functionality for conversation {conversation_id}"}

@app.get("/api/v1/chat/health")
async def chat_service_health():
    """Check chat service health including OpenAI connection"""
    return {
        "chat_service": "active",
        "openai_api": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
        "websocket_connections": "active"
    }

if __name__ == "__main__":
    # Load environment variables
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting OpenAI ChatBot API on {host}:{port}")
    logger.info("Make sure to set OPENAI_API_KEY environment variable for chat functionality")
    
    uvicorn.run(
        "chat_service.app:app", 
        host=host, 
        port=port, 
        reload=True,
        log_level="info"
    )
