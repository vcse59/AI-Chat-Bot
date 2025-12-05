"""
Conversation and message CRUD operations using utility functions
"""
# pylint: disable=logging-fstring-interpolation,broad-exception-caught
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from engine import models, schemas
from utilities.database_utils import (
    get_entity_by_id, get_entities_paginated,
    update_entity, delete_entity
)
from utilities.datetime_utils import get_utc_now
from utilities.logging_utils import log_database_operation
from utilities.hash_utils import (
    generate_conversation_hash, generate_message_hash
)
import logging

logger = logging.getLogger(__name__)

# Conversation CRUD operations
def create_conversation(db: Session, conversation: schemas.ConversationCreate) -> models.Conversation:
    """Create new conversation"""
    try:
        # Generate hash ID for conversation
        conversation_id = generate_conversation_hash(
            conversation.user_id or "anonymous", 
            conversation.title
        )
        
        # Create conversation with hash ID
        conversation_data = conversation.model_dump()
        conversation_data['id'] = conversation_id
        db_conversation = models.Conversation(**conversation_data)
        
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        
        log_database_operation(
            logger, "create", "conversations", conversation_id, 
            user_id=conversation.user_id, success=True
        )
        return db_conversation
        
    except Exception as e:
        log_database_operation(
            logger, "create", "conversations", user_id=conversation.user_id, 
            error=str(e), success=False
        )
        raise

def get_conversation(db: Session, conversation_id: str) -> Optional[models.Conversation]:
    """Get conversation by ID"""
    conversation = get_entity_by_id(db, models.Conversation, conversation_id)
    log_database_operation(
        logger, "read", "conversations", conversation_id, 
        success=conversation is not None
    )
    return conversation

def get_conversations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[str] = None,
    status: Optional[str] = None
) -> List[models.Conversation]:
    """Get conversations with filtering"""
    filters = {}
    if user_id is not None:
        filters["user_id"] = user_id
    if status is not None:
        filters["status"] = status
    
    conversations = get_entities_paginated(
        db, 
        models.Conversation, 
        skip=skip, 
        limit=limit, 
        filters=filters,
        order_by="created_at"
    )
    
    log_database_operation(
        logger, "read", "conversations", user_id=user_id, success=True
    )
    return conversations

def get_conversation_with_messages(db: Session, conversation_id: str) -> Optional[models.Conversation]:
    """Get conversation with its messages"""
    conversation = get_entity_by_id(db, models.Conversation, conversation_id)
    if conversation:
        # Messages will be loaded through the relationship
        log_database_operation(
            logger, "read", "conversations", conversation_id, success=True
        )
    return conversation

def update_conversation(
    db: Session, 
    conversation_id: str, 
    conversation: schemas.ConversationUpdate
) -> Optional[models.Conversation]:
    """Update conversation"""
    try:
        db_conversation = get_entity_by_id(db, models.Conversation, conversation_id)
        if not db_conversation:
            return None
        
        update_data = conversation.model_dump(exclude_unset=True)
        updated_conversation = update_entity(db, db_conversation, update_data)
        
        log_database_operation(
            logger, "update", "conversations", conversation_id, success=True
        )
        return updated_conversation
        
    except Exception as e:
        log_database_operation(
            logger, "update", "conversations", conversation_id, 
            error=str(e), success=False
        )
        raise

def end_conversation(db: Session, conversation_id: str) -> Optional[models.Conversation]:
    """End a conversation by setting status and end time"""
    try:
        db_conversation = get_entity_by_id(db, models.Conversation, conversation_id)
        if not db_conversation:
            return None
        
        update_data = {
            "status": "ended",
            "ended_at": get_utc_now()
        }
        
        updated_conversation = update_entity(db, db_conversation, update_data)
        
        log_database_operation(
            logger, "update", "conversations", conversation_id, success=True
        )
        return updated_conversation
        
    except Exception as e:
        log_database_operation(
            logger, "update", "conversations", conversation_id, 
            error=str(e), success=False
        )
        raise

def delete_conversation(db: Session, conversation_id: str) -> bool:
    """Delete conversation (and cascade to messages)"""
    try:
        success = delete_entity(db, models.Conversation, conversation_id)
        log_database_operation(
            logger, "delete", "conversations", conversation_id, success=success
        )
        return success
        
    except Exception as e:
        log_database_operation(
            logger, "delete", "conversations", conversation_id, 
            error=str(e), success=False
        )
        return False

# Chat Message CRUD operations
def create_message(db: Session, message: schemas.ChatMessageCreate) -> models.ChatMessage:
    """Create new chat message"""
    try:
        # Generate hash ID for message
        message_id = generate_message_hash(
            message.conversation_id, 
            message.content, 
            message.role
        )
        
        # Create message with hash ID
        message_data = message.model_dump()
        message_data['id'] = message_id
        db_message = models.ChatMessage(**message_data)
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        log_database_operation(
            logger, "create", "chat_messages", message_id, 
            success=True
        )
        return db_message
        
    except Exception as e:
        log_database_operation(
            logger, "create", "chat_messages", error=str(e), success=False
        )
        raise

def get_conversation_messages(
    db: Session, 
    conversation_id: str, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[str] = None
) -> List[models.ChatMessage]:
    """Get messages for a conversation with optional role filtering"""
    try:
        query = db.query(models.ChatMessage).filter(
            models.ChatMessage.conversation_id == conversation_id
        )
        
        if role:
            query = query.filter(models.ChatMessage.role == role)
        
        messages = query.order_by(
            models.ChatMessage.timestamp.asc()
        ).offset(skip).limit(limit).all()
        
        log_database_operation(
            logger, "read", "chat_messages", success=True
        )
        return messages
        
    except Exception as e:
        log_database_operation(
            logger, "read", "chat_messages", error=str(e), success=False
        )
        raise

def get_message(db: Session, message_id: str) -> Optional[models.ChatMessage]:
    """Get message by ID"""
    message = get_entity_by_id(db, models.ChatMessage, message_id)
    log_database_operation(
        logger, "read", "chat_messages", message_id, 
        success=message is not None
    )
    return message

def delete_message(db: Session, message_id: str) -> bool:
    """Delete message"""
    try:
        success = delete_entity(db, models.ChatMessage, message_id)
        log_database_operation(
            logger, "delete", "chat_messages", message_id, success=success
        )
        return success
        
    except Exception as e:
        log_database_operation(
            logger, "delete", "chat_messages", message_id, 
            error=str(e), success=False
        )
        return False

def get_recent_messages(
    db: Session, 
    conversation_id: str, 
    limit: int = 10
) -> List[models.ChatMessage]:
    """Get recent messages from a conversation for context"""
    try:
        messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.conversation_id == conversation_id
        ).order_by(
            models.ChatMessage.timestamp.desc()
        ).limit(limit).all()
        
        # Return in chronological order (oldest first)
        messages.reverse()
        
        log_database_operation(
            logger, "read", "chat_messages", success=True
        )
        return messages
        
    except Exception as e:
        log_database_operation(
            logger, "read", "chat_messages", error=str(e), success=False
        )
        return []

def get_conversation_stats(db: Session, conversation_id: str) -> Dict[str, Any]:
    """Get statistics for a conversation"""
    try:
        # Count total messages
        total_messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.conversation_id == conversation_id
        ).count()
        
        # Count by role
        user_messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.conversation_id == conversation_id,
            models.ChatMessage.role == "user"
        ).count()
        
        assistant_messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.conversation_id == conversation_id,
            models.ChatMessage.role == "assistant"
        ).count()
        
        # Get total tokens used
        total_tokens = db.query(
            models.ChatMessage.tokens_used
        ).filter(
            models.ChatMessage.conversation_id == conversation_id,
            models.ChatMessage.tokens_used.isnot(None)
        ).all()
        
        tokens_sum = sum(tokens[0] for tokens in total_tokens if tokens[0])
        
        stats = {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_tokens_used": tokens_sum
        }
        
        log_database_operation(
            logger, "read", "conversations", conversation_id, success=True
        )
        return stats
        
    except Exception as e:
        log_database_operation(
            logger, "read", "conversations", conversation_id, 
            error=str(e), success=False
        )
        return {}