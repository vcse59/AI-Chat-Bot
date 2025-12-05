# pylint: disable=logging-fstring-interpolation,broad-exception-caught
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from engine.database import get_database
from engine import schemas, crud
from engine import mcp_server_crud
from security import get_current_active_user, require_admin, CurrentUser
from middleware.analytics_middleware import (
    track_conversation, track_message, sync_user_profile, delete_user_analytics
)
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get database session
def get_db():
    db = next(get_database())
    try:
        yield db
    finally:
        db.close()

# Note: User CRUD operations are handled by auth-service
# Auth-service provides the following endpoints:
# - POST   /api/v1/users/           - Create user
# - GET    /api/v1/users/           - List all users (admin only)
# - GET    /api/v1/users/me         - Get current user
# - GET    /api/v1/users/{username} - Get specific user
# - PUT    /api/v1/users/{username} - Update user
# - DELETE /api/v1/users/{username} - Delete user (admin only)


# Message endpoints for conversations
@router.post("/conversations/{conversation_id}/messages/", response_model=schemas.ChatMessageResponse, tags=["messages"])
async def create_message(
    conversation_id: str,
    message: schemas.ChatMessageCreateSimple,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Add a message to a conversation (Must own the conversation or be Admin)"""
    # Verify conversation exists
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get user by username to compare with conversation owner
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only add messages to their own conversations unless they're admin
    if not current_user.is_admin() and str(user.id) != str(conversation.user_id):
        raise HTTPException(status_code=403, detail="Access denied: Can only add messages to your own conversations")
    
    # Create the full message with conversation_id
    full_message = schemas.ChatMessageCreate(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
        model=message.model,
        tokens_used=message.tokens_used,
        message_metadata=message.message_metadata
    )
    created_message = crud.create_message(db=db, message=full_message)
    
    # Only track assistant messages (actual OpenAI interactions) in analytics
    # User messages via REST API don't involve OpenAI calls, so we don't track them
    if message.role == "assistant" and message.tokens_used:
        asyncio.create_task(track_message(
            message_id=str(created_message.id),
            conversation_id=str(conversation_id),
            user_id=str(user.id),
            role=message.role,
            token_count=message.tokens_used or 0,
            response_time=None,  # REST API doesn't have OpenAI response time
            model_used=message.model
        ))
    
    return created_message

@router.get("/conversations/{conversation_id}/messages/", response_model=List[schemas.ChatMessageResponse], tags=["messages"])
async def read_conversation_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Get messages for a specific conversation (Must own the conversation or be Admin)"""
    # Verify conversation exists
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get user by username to compare with conversation owner
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only view messages from their own conversations unless they're admin
    if not current_user.is_admin() and str(user.id) != str(conversation.user_id):
        raise HTTPException(status_code=403, detail="Access denied: Can only view messages from your own conversations")
    
    messages = crud.get_conversation_messages(db, conversation_id=conversation_id, skip=skip, limit=limit)
    return messages



# User conversation management
@router.post("/users/{user_id}/conversations/", response_model=schemas.ConversationResponse, tags=["user-conversations"])
async def create_user_conversation(
    user_id: str,
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Create a new conversation for a specific user (Authenticated users only)"""
    # Verify user exists, create if not (auto-provision authenticated users)
    user = crud.get_user(db, user_id=user_id)
    if not user:
        # Auto-create user in chat database from authenticated token info
        user_create = schemas.UserCreate(
            username=current_user.username,
            email=f"{current_user.username}@chatbot.example.com",  # Auto-generated email
            full_name=current_user.username
        )
        try:
            user = crud.create_user(db=db, user=user_create)
        except Exception as e:
            # If creation fails (e.g., user exists with different ID), try to get by username
            user = crud.get_user_by_username(db, current_user.username)
            if not user:
                raise HTTPException(status_code=500, detail=f"Could not provision user: {str(e)}")
    
    # Users can only create conversations for themselves unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only create conversations for yourself")
    
    # Set the user_id in the conversation data
    conversation.user_id = str(user.id)
    created_conversation = crud.create_conversation(db=db, conversation=conversation)
    
    # Sync user profile with analytics (include role info from token if available)
    user_role = None
    if hasattr(current_user, 'roles') and current_user.roles:
        user_role = "admin" if "admin" in current_user.roles else "user"
    
    asyncio.create_task(sync_user_profile(
        user_id=str(user.id),
        username=str(user.username),
        role=user_role,
        email=str(user.email) if hasattr(user, 'email') and user.email is not None else None
    ))
    
    # Track conversation creation in analytics
    asyncio.create_task(track_conversation(
        conversation_id=str(created_conversation.id),
        user_id=str(user.id),
        action="created"
    ))
    
    return created_conversation

@router.get("/users/{user_id}/conversations/", response_model=List[schemas.ConversationResponse], tags=["user-conversations"])
async def get_user_conversations(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[schemas.ConversationStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Get all conversations for a specific user (Own conversations or Admin)"""
    # Verify user exists, create if not (auto-provision authenticated users)
    user = crud.get_user(db, user_id=user_id)
    if not user:
        # Auto-create user in chat database from authenticated token info
        user_create = schemas.UserCreate(
            username=current_user.username,
            email=f"{current_user.username}@chatbot.example.com",  # Auto-generated email
            full_name=current_user.username
        )
        try:
            user = crud.create_user(db=db, user=user_create)
        except Exception as e:
            # If creation fails, try to get by username
            user = crud.get_user_by_username(db, current_user.username)
            if not user:
                raise HTTPException(status_code=500, detail=f"Could not provision user: {str(e)}")
    
    # Users can only view their own conversations unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only view your own conversations")
    
    conversations = crud.get_conversations(db, skip=skip, limit=limit, user_id=str(user.id), status=status)
    return conversations

# Reconnection endpoints
@router.post("/users/{user_id}/conversations/{conversation_id}/reconnect", response_model=schemas.ConversationWithMessages, tags=["reconnection"])
async def reconnect_to_conversation(
    user_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Reconnect user to an existing conversation - validates ownership and returns conversation with recent messages (Own conversation or Admin)"""
    # Verify user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only reconnect to their own conversations unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only reconnect to your own conversations")
    
    # Get conversation with messages
    conversation = crud.get_conversation_with_messages(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Admins can reconnect to any conversation, non-admins must own it
    if not current_user.is_admin():
        # Verify user owns this conversation - compare as strings using user.id not path param
        if str(conversation.user_id) != str(user.id):
            raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    
    # Update conversation status to active if it was ended
    if conversation.status.value == schemas.ConversationStatus.ENDED.value:
        conversation_update = schemas.ConversationUpdate(status=schemas.ConversationStatus.ACTIVE)
        conversation = crud.update_conversation(db, conversation_id=conversation_id, conversation=conversation_update)
    
    return conversation

@router.get("/users/{user_id}/conversations/{conversation_id}/validate", tags=["reconnection"])
async def validate_conversation_access(
    user_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Validate if user can access a specific conversation (Own conversation or Admin)"""
    # Verify user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only validate their own conversations unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only validate your own conversations")
    
    # Get conversation
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Admins can validate any conversation, non-admins must own it
    if not current_user.is_admin():
        # Check ownership - compare as strings using user.id not path param
        if str(conversation.user_id) != str(user.id):
            raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    
    return {
        "valid": True,
        "conversation_id": conversation_id,
        "user_id": user_id,
        "conversation_title": conversation.title,
        "conversation_status": conversation.status,
        "created_at": conversation.created_at,
        "message": "Access granted - you can reconnect to this conversation"
    }

@router.get("/users/{user_id}/conversations/recent", response_model=List[schemas.ConversationResponse], tags=["reconnection"])
async def get_user_recent_conversations(
    user_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Get user's most recent conversations for easy reconnection (Own conversations or Admin)"""
    # Verify user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only view their own conversations unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only view your own conversations")
    
    conversations = crud.get_conversations(db, skip=0, limit=limit, user_id=user_id)
    return conversations

@router.post("/users/{user_id}/conversations/{conversation_id}/end", response_model=schemas.ConversationResponse, tags=["user-conversations"])
async def end_user_conversation(
    user_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """End a conversation for a specific user (Own conversation or Admin)"""
    # Verify user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only end their own conversations unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only end your own conversations")
    
    # Verify conversation exists and user owns it
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Admins can end any conversation, non-admins must own it
    if not current_user.is_admin():
        # Compare as strings and use user.id not path parameter user_id
        if str(conversation.user_id) != str(user.id):
            raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    
    # End the conversation
    db_conversation = crud.end_conversation(db, conversation_id=conversation_id)
    return db_conversation

@router.delete("/users/{user_id}/conversations/{conversation_id}", tags=["user-conversations"])
async def delete_user_conversation(
    user_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Delete a conversation for a specific user (Own conversation or Admin)"""
    logger.info(f"=== DELETE ENDPOINT CALLED ===")
    logger.info(f"Path params - user_id: {user_id}, conversation_id: {conversation_id}")
    logger.info(f"Current user - username: {current_user.username}, is_admin: {current_user.is_admin()}, roles: {current_user.roles}")
    
    # Get user by username first (since user_id in path might be username)
    user = crud.get_user_by_username(db, user_id)
    if not user:
        # Try as actual user ID
        user = crud.get_user(db, user_id=user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify conversation exists
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Admins can delete any conversation, regular users can only delete their own
    logger.info(f"Delete check - current_user: {current_user.username}, roles: {current_user.roles}, is_admin: {current_user.is_admin()}")
    logger.info(f"Delete check - target_user: {user.username}, conversation_owner: {conversation.user_id}")
    
    if not current_user.is_admin():
        # Non-admin users must own the conversation
        if current_user.username != user.username:
            raise HTTPException(status_code=403, detail="Access denied: Can only delete your own conversations")
        
        # Verify ownership - compare as strings to handle type mismatches
        if str(conversation.user_id) != str(user.id):
            raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    else:
        logger.info("Admin user - bypassing ownership checks")
    
    # Delete the conversation
    success = crud.delete_conversation(db, conversation_id=conversation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
    
    # Track conversation deletion in analytics
    asyncio.create_task(track_conversation(
        conversation_id=conversation_id,
        user_id=str(user.id),
        action="deleted"
    ))
    
    return {"message": "Conversation deleted successfully", "conversation_id": conversation_id}

@router.get("/users/{user_id}/conversations/{conversation_id}/stats", tags=["user-conversations"])
async def get_user_conversation_stats(
    user_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Get conversation statistics for a user's conversation (Own conversation or Admin)"""
    # Verify user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only view their own conversation stats unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only view your own conversation statistics")
    
    # Verify conversation exists and user owns it
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if str(conversation.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    
    stats = crud.get_conversation_stats(db, conversation_id=conversation_id)
    return stats


# Admin-only endpoints
@router.get("/admin/conversations/", response_model=List[schemas.ConversationResponse], tags=["admin"])
async def get_all_conversations_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """Get all conversations across all users (Admin only)"""
    # Get all conversations without user filtering (user_id=None gets all)
    conversations = crud.get_conversations(db, skip=skip, limit=limit, user_id=None)
    return conversations


@router.delete("/admin/conversations/{conversation_id}", tags=["admin"])
async def delete_conversation_admin(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """Delete any conversation regardless of owner (Admin only)"""
    # Verify conversation exists
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Admin can delete any conversation - no ownership check needed
    success = crud.delete_conversation(db, conversation_id=conversation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
    
    # Track conversation deletion in analytics
    asyncio.create_task(track_conversation(
        conversation_id=str(conversation_id),
        user_id=str(conversation.user_id),
        action="deleted"
    ))
    
    return {"message": "Conversation deleted successfully by admin", "conversation_id": conversation_id}


@router.delete("/admin/users/{username}", tags=["admin"])
async def delete_user_admin(
    username: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """Delete a user and all their data (Admin only)
    
    This endpoint deletes:
    - User record from chat database
    - All user's conversations and messages
    - User's MCP server configurations
    - User's analytics data
    """
    # Find user by username
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    
    user_id = str(user.id)
    
    # Delete all user's conversations first (cascade will handle messages)
    conversations = crud.get_conversations(db, user_id=user_id, limit=10000)
    for conv in conversations:
        crud.delete_conversation(db, conversation_id=str(conv.id))
    
    # Delete user's MCP servers
    mcp_servers = mcp_server_crud.get_user_mcp_servers(db, user_id=user_id)
    for server in mcp_servers:
        mcp_server_crud.delete_mcp_server(db, server_id=str(server.id))
    
    # Delete the user from chat database
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    
    # Delete user's analytics data (async, non-blocking)
    auth_header = request.headers.get("Authorization", "")
    auth_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    asyncio.create_task(delete_user_analytics(username, auth_token))
    
    return {"message": f"User '{username}' and all associated data deleted successfully"}


# ============================================================================
# MCP Server Management Endpoints
# ============================================================================

@router.post("/mcp-servers/", response_model=schemas.MCPServerResponse, tags=["mcp-servers"])
async def create_mcp_server(
    mcp_server: schemas.MCPServerCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Create a new MCP server configuration"""
    # Get user from database
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create MCP server for the authenticated user
    created_server = mcp_server_crud.create_mcp_server(db, mcp_server, str(user.id))
    return created_server

@router.get("/mcp-servers/", response_model=List[schemas.MCPServerResponse], tags=["mcp-servers"])
async def list_user_mcp_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """List all MCP servers for the current user"""
    # Get user from database
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's MCP servers
    servers = mcp_server_crud.get_user_mcp_servers(db, str(user.id), skip, limit, active_only)
    return servers

@router.get("/mcp-servers/{server_id}", response_model=schemas.MCPServerResponse, tags=["mcp-servers"])
async def get_mcp_server(
    server_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Get a specific MCP server by ID"""
    server = mcp_server_crud.get_mcp_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    # Get user from database
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check ownership or admin access
    if not current_user.is_admin() and str(server.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied: Not your MCP server")
    
    return server

@router.put("/mcp-servers/{server_id}", response_model=schemas.MCPServerResponse, tags=["mcp-servers"])
async def update_mcp_server(
    server_id: str,
    mcp_server_update: schemas.MCPServerUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Update an MCP server configuration"""
    server = mcp_server_crud.get_mcp_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    # Get user from database
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check ownership or admin access
    if not current_user.is_admin() and str(server.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied: Not your MCP server")
    
    # Update server
    updated_server = mcp_server_crud.update_mcp_server(db, server_id, mcp_server_update)
    return updated_server

@router.delete("/mcp-servers/{server_id}", tags=["mcp-servers"])
async def delete_mcp_server(
    server_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """Delete an MCP server"""
    server = mcp_server_crud.get_mcp_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    # Get user from database
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check ownership or admin access
    if not current_user.is_admin() and str(server.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied: Not your MCP server")
    
    # Delete server
    success = mcp_server_crud.delete_mcp_server(db, server_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete MCP server")
    
    return {"message": "MCP server deleted successfully", "server_id": server_id}

@router.get("/admin/mcp-servers/", response_model=List[schemas.MCPServerResponse], tags=["mcp-servers", "admin"])
async def list_all_mcp_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """List all MCP servers across all users (Admin only)"""
    servers = mcp_server_crud.get_all_mcp_servers(db, skip, limit, active_only)
    return servers
