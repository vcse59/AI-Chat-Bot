"""Analytics data models for tracking usage and metrics"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime
from analytics.database.db import Base


class UserActivity(Base):
    """Track user login and activity metrics"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    activity_type = Column(String, nullable=False)  # login, logout, api_call, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    extra_data = Column(JSON, nullable=True)


class ConversationMetrics(Base):
    """Track conversation-level analytics"""
    __tablename__ = "conversation_metrics"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)  # in seconds
    status = Column(String, default="active")  # active, archived, deleted


class MessageMetrics(Base):
    """Track individual message analytics"""
    __tablename__ = "message_metrics"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, index=True, nullable=False)
    conversation_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    token_count = Column(Integer, default=0)
    response_time = Column(Float, nullable=True)  # in seconds
    model_used = Column(String, nullable=True)
    cost = Column(Float, default=0.0)


class APIUsage(Base):
    """Track API endpoint usage and performance"""
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True, nullable=False)
    method = Column(String, nullable=False)  # GET, POST, PUT, DELETE
    user_id = Column(String, index=True, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=False)  # in seconds
    error_message = Column(Text, nullable=True)


class SystemMetrics(Base):
    """Track system-wide metrics and health"""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    extra_data = Column(JSON, nullable=True)


class DailyStats(Base):
    """Aggregated daily statistics"""
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True, nullable=False, unique=True)
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_api_calls = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
