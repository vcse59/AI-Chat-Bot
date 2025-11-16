from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from engine.database import get_database
from engine import schemas, crud
from security import get_current_user, get_current_active_user, require_admin, CurrentUser
from middleware.analytics_middleware import track_conversation, track_message
import asyncio

router = APIRouter()

# Dependency to get database session
def get_db():
    db = next(get_database())
    try:
        yield db
    finally:
        db.close()

# User CRUD endpoints
@router.post("/users/", response_model=schemas.UserResponse, tags=["users"])
async def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """Create a new user (Admin only)"""
    # Check if user already exists
    existing_user = crud.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = crud.get_user_by_username(db, username=user.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.UserResponse], tags=["users"])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """Get all users with pagination (Admin only)"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["users"])
async def read_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: Optional[CurrentUser] = Depends(get_current_user)
):
    """Get a specific user by ID (Authenticated users can view)"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=schemas.UserResponse, tags=["users"])
async def update_user(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = crud.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete a user"""
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}





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
    if not current_user.is_admin() and user.id != conversation.user_id:
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
    
    # Track message creation in analytics
    asyncio.create_task(track_message(
        message_id=created_message.id,
        conversation_id=conversation_id,
        user_id=user.id,
        role=message.role,
        token_count=message.tokens_used or 0,
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
    if not current_user.is_admin() and user.id != conversation.user_id:
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
    conversation.user_id = user.id
    created_conversation = crud.create_conversation(db=db, conversation=conversation)
    
    # Track conversation creation in analytics
    asyncio.create_task(track_conversation(
        conversation_id=created_conversation.id,
        user_id=user.id,
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
    
    conversations = crud.get_conversations(db, skip=skip, limit=limit, user_id=user.id, status=status)
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
    
    # Verify user owns this conversation
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    
    # Update conversation status to active if it was ended
    if conversation.status == schemas.ConversationStatus.ENDED:
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
    
    # Check ownership
    if conversation.user_id != user_id:
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
    
    if conversation.user_id != user_id:
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
    # Get user by username first (since user_id in path might be username)
    user = crud.get_user_by_username(db, user_id)
    if not user:
        # Try as actual user ID
        user = crud.get_user(db, user_id=user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only delete their own conversations unless they're admin
    if not current_user.is_admin() and current_user.username != user.username:
        raise HTTPException(status_code=403, detail="Access denied: Can only delete your own conversations")
    
    # Verify conversation exists and user owns it
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    
    # Delete the conversation
    success = crud.delete_conversation(db, conversation_id=conversation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
    
    # Track conversation deletion in analytics
    asyncio.create_task(track_conversation(
        conversation_id=conversation_id,
        user_id=user.id,
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
    
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this conversation")
    
    stats = crud.get_conversation_stats(db, conversation_id=conversation_id)
    return stats