"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ConversationStartRequest(BaseModel):
    """Request to start a new conversation"""
    user_id: Optional[str] = None
    title: Optional[str] = None
    system_message: Optional[str] = None
    workflow_type: str = Field(default="simple_chain", pattern="^(simple_chain|structured_chain|summary_memory)$")


class MessageRequest(BaseModel):
    """Request to send a message"""
    message: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None


class StructuredMessageRequest(BaseModel):
    """Request for structured chain processing"""
    message: str = Field(..., min_length=1)
    chain_type: str = Field(default="qa", pattern="^(qa|summarize|extract)$")
    context: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Response from workflow processing"""
    conversation_id: str
    user_message: Dict[str, Any]
    ai_response: Dict[str, Any]
    response_time_ms: int
    tokens_used: Optional[int] = None
    workflow_type: str
    metadata: Optional[Dict[str, Any]] = None


class ConversationSummaryResponse(BaseModel):
    """Response containing conversation summary"""
    conversation_id: str
    summary: str
    message_count: int
    tokens_used: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    chat_service_connected: bool
    openai_configured: bool
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
