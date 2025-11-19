from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from engine.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(12), primary_key=True, index=True)  # Hash-based ID
    user_id = Column(String(16), ForeignKey("users.id"), nullable=True)  # Hash-based foreign key
    title = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active, ended, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Metadata for conversation context
    context_metadata = Column(JSON, nullable=True)
    
    # Relationship with messages
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(10), primary_key=True, index=True)  # Hash-based ID
    conversation_id = Column(String(12), ForeignKey("conversations.id"), nullable=False)  # Hash-based foreign key
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # OpenAI specific fields
    model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Integer, nullable=True)  # Response time in milliseconds
    
    # Metadata for additional context
    message_metadata = Column(JSON, nullable=True)
    
    # Relationship with conversation
    conversation = relationship("Conversation", back_populates="messages")

class User(Base):
    __tablename__ = "users"

    id = Column(String(16), primary_key=True, index=True)  # Hash-based ID
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with conversations
    conversations = relationship("Conversation", backref="user")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=True)  # Price in cents
    is_available = Column(Boolean, default=True)
    owner_id = Column(String(16), ForeignKey("users.id"))  # Hash-based foreign key
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with user
    owner = relationship("User", backref="items")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(String(12), primary_key=True, index=True)  # Hash-based ID
    user_id = Column(String(16), ForeignKey("users.id"), nullable=False)  # Hash-based foreign key
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    server_url = Column(String(500), nullable=False)
    auth_type = Column(String(50), default="none")  # Authentication type: none, bearer, api_key
    api_key = Column(String(500), nullable=True)  # Optional API key for MCP server
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)  # Additional configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with user
    owner = relationship("User", backref="mcp_servers")