from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    ARCHIVED = "archived"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str  # Hash-based ID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Item Schemas
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)  # Price in cents, must be >= 0
    is_available: bool = True

class ItemCreate(ItemBase):
    owner_id: Optional[str] = None  # Hash-based owner ID

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None

class ItemResponse(ItemBase):
    id: int
    owner_id: Optional[str]  # Hash-based owner ID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# User with items relationship
class UserWithItems(UserResponse):
    items: List[ItemResponse] = []

# Conversation Schemas
class ConversationBase(BaseModel):
    title: Optional[str] = None
    user_id: Optional[str] = None  # Hash-based user ID
    context_metadata: Optional[Dict[str, Any]] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    context_metadata: Optional[Dict[str, Any]] = None

class ConversationResponse(ConversationBase):
    id: str  # Hash-based ID
    status: ConversationStatus
    created_at: datetime
    ended_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Chat Message Schemas
class ChatMessageBase(BaseModel):
    role: MessageRole
    content: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[int] = None  # Response time in milliseconds
    message_metadata: Optional[Dict[str, Any]] = None

class ChatMessageCreate(ChatMessageBase):
    conversation_id: str  # Hash-based conversation ID

class ChatMessageCreateSimple(BaseModel):
    """Simplified message creation schema without conversation_id (provided in URL)"""
    role: MessageRole
    content: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[int] = None  # Response time in milliseconds
    message_metadata: Optional[Dict[str, Any]] = None

class ChatMessageResponse(ChatMessageBase):
    id: str  # Hash-based ID
    conversation_id: str  # Hash-based conversation ID
    timestamp: datetime

    class Config:
        from_attributes = True

# WebSocket Message Schemas
class WebSocketMessage(BaseModel):
    type: str  # "start_conversation", "send_message", "end_conversation"
    data: Dict[str, Any]

class StartConversationRequest(BaseModel):
    user_id: Optional[str] = None  # Hash-based user ID
    title: Optional[str] = None
    system_message: Optional[str] = None

class SendMessageRequest(BaseModel):
    conversation_id: str  # Hash-based conversation ID
    content: str

class EndConversationRequest(BaseModel):
    conversation_id: str  # Hash-based conversation ID

# WebSocket Response Schemas
class WebSocketResponse(BaseModel):
    type: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Conversation with Messages
class ConversationWithMessages(ConversationResponse):
    messages: List[ChatMessageResponse] = []

# Response models for paginated results
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

# MCP Server Schemas
class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    server_url: str = Field(..., min_length=1, max_length=500)
    is_active: bool = True
    config: Optional[Dict[str, Any]] = None

class MCPServerCreate(MCPServerBase):
    pass

class MCPServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    server_url: Optional[str] = Field(None, min_length=1, max_length=500)
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class MCPServerResponse(MCPServerBase):
    id: str  # Hash-based ID
    user_id: str  # Hash-based user ID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True