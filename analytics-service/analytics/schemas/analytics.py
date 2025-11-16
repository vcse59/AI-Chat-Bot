"""Pydantic schemas for analytics data"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any


class UserActivitySchema(BaseModel):
    """Schema for user activity data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: str
    username: str
    activity_type: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class ConversationMetricsSchema(BaseModel):
    """Schema for conversation metrics"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    conversation_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    total_tokens: int
    avg_response_time: float
    status: str


class MessageMetricsSchema(BaseModel):
    """Schema for message metrics"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    message_id: str
    conversation_id: str
    user_id: str
    role: str
    timestamp: datetime
    token_count: int
    response_time: Optional[float] = None
    model_used: Optional[str] = None
    cost: float


class APIUsageSchema(BaseModel):
    """Schema for API usage data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    endpoint: str
    method: str
    user_id: Optional[str] = None
    timestamp: datetime
    status_code: int
    response_time: float
    error_message: Optional[str] = None


class DailyStatsSchema(BaseModel):
    """Schema for daily statistics"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date: datetime
    total_users: int
    active_users: int
    new_users: int
    total_conversations: int
    total_messages: int
    total_tokens: int
    total_api_calls: int
    avg_response_time: float
    error_count: int
    created_at: datetime


class AnalyticsSummary(BaseModel):
    """Summary analytics response"""
    total_users: int
    active_users_today: int
    total_conversations: int
    total_messages: int
    total_tokens: int
    total_api_calls: int
    avg_response_time: float
    error_rate: float


class TimeRangeQuery(BaseModel):
    """Query parameters for time-based analytics"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
