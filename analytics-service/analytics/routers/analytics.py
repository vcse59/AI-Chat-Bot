"""Analytics API endpoints - Admin access only"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from analytics.database.db import get_db
from analytics.security.auth import require_admin, CurrentUser
from analytics.schemas.analytics import (
    UserActivitySchema,
    ConversationMetricsSchema,
    APIUsageSchema,
    DailyStatsSchema,
    AnalyticsSummary
)
from analytics.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/test-auth")
async def test_auth(request: Request):
    """Test endpoint to check authorization header"""
    auth_header = request.headers.get("authorization", "NOT FOUND")
    logger.info(f"Authorization header: {auth_header[:50] if auth_header != 'NOT FOUND' else auth_header}...")
    return {
        "message": "Test endpoint",
        "auth_header_present": auth_header != "NOT FOUND",
        "auth_header_preview": auth_header[:100] if auth_header != "NOT FOUND" else "NOT FOUND"
    }


@router.get("/", response_model=dict)
async def analytics_root(
    current_user: CurrentUser = Depends(require_admin)
):
    """Analytics API root - Admin only"""
    return {
        "message": "Analytics API",
        "version": "1.0.0",
        "user": current_user.username,
        "role": "admin"
    }


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get overall analytics summary.
    
    **Admin access required**
    
    Returns:
        - Total users
        - Active users today
        - Total conversations
        - Total messages
        - Total API calls
        - Average response time
        - Error rate
    """
    return AnalyticsService.get_summary(db)


@router.get("/users/activities", response_model=List[UserActivitySchema])
async def get_user_activities(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get user activity logs.
    
    **Admin access required**
    
    Query parameters:
        - user_id: Filter by specific user
        - start_date: Start date for filtering
        - end_date: End date for filtering
        - limit: Maximum number of results (1-1000)
    """
    return AnalyticsService.get_user_activities(
        db, user_id=user_id, start_date=start_date, end_date=end_date, limit=limit
    )


@router.get("/users/top", response_model=List[dict])
async def get_top_users(
    limit: int = Query(10, ge=1, le=100, description="Number of top users to return"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get top users by activity count.
    
    **Admin access required**
    """
    return AnalyticsService.get_top_users(db, limit=limit)


@router.get("/users/list", response_model=List[dict])
async def get_users_list(
    active_only: bool = Query(False, description="Show only active users (with activity today)"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all users with their activity count.
    
    **Admin access required**
    
    Query parameters:
        - active_only: If true, only return users with activity today
    """
    from analytics.models.analytics import UserActivity
    from datetime import datetime
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    query = db.query(
        UserActivity.user_id,
        UserActivity.username,
        func.count(UserActivity.id).label('activity_count'),
        func.max(UserActivity.timestamp).label('last_activity')
    ).group_by(
        UserActivity.user_id,
        UserActivity.username
    )
    
    if active_only:
        query = query.having(func.max(UserActivity.timestamp) >= today)
    
    results = query.order_by(func.max(UserActivity.timestamp).desc()).all()
    
    return [
        {
            "user_id": r.user_id,
            "username": r.username,
            "activity_count": r.activity_count,
            "last_activity": r.last_activity.isoformat(),
            "is_active_today": r.last_activity >= today
        }
        for r in results
    ]


@router.get("/conversations", response_model=List[ConversationMetricsSchema])
async def get_conversation_metrics(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get conversation metrics.
    
    **Admin access required**
    
    Returns metrics for conversations including:
        - Message count
        - Total tokens used
        - Average response time
        - Status
    """
    return AnalyticsService.get_conversation_metrics(db, user_id=user_id, limit=limit)


@router.get("/api-usage", response_model=List[APIUsageSchema])
async def get_api_usage(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get API usage statistics.
    
    **Admin access required**
    
    Returns:
        - Endpoint
        - Method
        - Response time
        - Status code
        - Errors
    """
    return AnalyticsService.get_api_usage_stats(
        db, start_date=start_date, end_date=end_date, endpoint=endpoint
    )


@router.get("/daily-stats", response_model=List[DailyStatsSchema])
async def get_daily_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get daily aggregated statistics.
    
    **Admin access required**
    
    Returns daily stats for the specified number of days including:
        - Total and active users
        - New users
        - Conversations and messages
        - API calls and performance
        - Error counts
    """
    return AnalyticsService.get_daily_stats(db, days=days)


@router.post("/track/activity")
async def track_user_activity_admin(
    activity_type: str,
    extra_data: Optional[dict] = None,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually track a user activity event.
    
    **Admin access required**
    """
    activity = AnalyticsService.log_user_activity(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        activity_type=activity_type,
        extra_data=extra_data
    )
    return {"message": "Activity logged", "activity_id": activity.id}


# Public tracking endpoints for service-to-service communication (no authentication)
from pydantic import BaseModel

class ActivityTrackingRequest(BaseModel):
    user_id: str
    username: str
    activity_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    extra_data: Optional[dict] = None

class APIUsageTrackingRequest(BaseModel):
    endpoint: str
    method: str
    user_id: Optional[str] = None
    status_code: int
    response_time: float

class ConversationTrackingRequest(BaseModel):
    conversation_id: str
    user_id: str
    action: str

class MessageTrackingRequest(BaseModel):
    message_id: str
    conversation_id: str
    user_id: str
    role: str
    token_count: Optional[int] = 0
    response_time: Optional[float] = None
    model_used: Optional[str] = None


@router.post("/track/activity-public")
async def track_activity_public(request: ActivityTrackingRequest, db: Session = Depends(get_db)):
    """Public endpoint for tracking user activities from other services"""
    from analytics.models.analytics import UserActivity
    activity = UserActivity(
        user_id=request.user_id,
        username=request.username,
        activity_type=request.activity_type,
        ip_address=request.ip_address,
        user_agent=request.user_agent,
        extra_data=request.extra_data
    )
    db.add(activity)
    db.commit()
    return {"status": "tracked"}


@router.post("/track/api-usage-public")
async def track_api_usage_public(request: APIUsageTrackingRequest, db: Session = Depends(get_db)):
    """Public endpoint for tracking API usage from other services"""
    from analytics.models.analytics import APIUsage
    usage = APIUsage(
        endpoint=request.endpoint,
        method=request.method,
        user_id=request.user_id,
        status_code=request.status_code,
        response_time=request.response_time
    )
    db.add(usage)
    db.commit()
    return {"status": "tracked"}


@router.post("/track/conversation-public")
async def track_conversation_public(request: ConversationTrackingRequest, db: Session = Depends(get_db)):
    """Public endpoint for tracking conversations from other services"""
    from analytics.models.analytics import ConversationMetrics, MessageMetrics
    
    if request.action == "created":
        conv = ConversationMetrics(
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            message_count=0,
            status="active"
        )
        db.add(conv)
    elif request.action == "deleted":
        # Delete all message metrics for this conversation
        db.query(MessageMetrics).filter(
            MessageMetrics.conversation_id == request.conversation_id
        ).delete()
        
        # Delete the conversation metrics
        db.query(ConversationMetrics).filter(
            ConversationMetrics.conversation_id == request.conversation_id
        ).delete()
    
    db.commit()
    return {"status": "tracked"}


@router.post("/track/message-public")
async def track_message_public(request: MessageTrackingRequest, db: Session = Depends(get_db)):
    """Public endpoint for tracking messages from other services"""
    from analytics.models.analytics import MessageMetrics, ConversationMetrics
    
    # Track the message
    message = MessageMetrics(
        message_id=request.message_id,
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        role=request.role,
        token_count=request.token_count,
        response_time=request.response_time,
        model_used=request.model_used
    )
    db.add(message)
    
    # Update conversation metrics
    conv = db.query(ConversationMetrics).filter(
        ConversationMetrics.conversation_id == request.conversation_id
    ).first()
    
    if conv:
        # Get current values
        current_message_count = int(conv.message_count)  # type: ignore
        current_total_tokens = int(conv.total_tokens)  # type: ignore
        current_avg_response = float(conv.avg_response_time) if conv.avg_response_time is not None else 0.0  # type: ignore
        
        # Increment message count
        new_message_count = current_message_count + 1
        
        # Add tokens
        new_total_tokens = current_total_tokens + (request.token_count or 0)
        
        # Calculate new average response time (weighted average)
        new_avg_response_time = current_avg_response
        if request.response_time is not None and request.response_time > 0:
            if current_avg_response == 0.0:
                new_avg_response_time = request.response_time
            else:
                # Weighted average: (old_avg * old_count + new_value) / new_count
                total_response_time = current_avg_response * current_message_count
                new_avg_response_time = (total_response_time + request.response_time) / new_message_count
        
        # Update conversation
        db.query(ConversationMetrics).filter(
            ConversationMetrics.conversation_id == request.conversation_id
        ).update({
            "message_count": new_message_count,
            "total_tokens": new_total_tokens,
            "avg_response_time": new_avg_response_time,
            "updated_at": datetime.utcnow()
        }, synchronize_session=False)
    
    db.commit()
    return {"status": "tracked"}


# Enhanced Analytics Endpoints

@router.get("/metrics/by-role", response_model=List[dict])
async def get_metrics_by_role(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get user metrics grouped by role.
    
    **Admin access required**
    
    Returns:
        - User count per role
        - Total conversations per role
        - Total messages per role
        - Total tokens per role
        - Average response time per role
    """
    return AnalyticsService.get_user_metrics_by_role(db)


@router.get("/users/detailed-metrics", response_model=List[dict])
async def get_users_detailed_metrics(
    user_id: Optional[str] = Query(None, description="Filter by specific user"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of users"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed metrics for all users or a specific user.
    
    **Admin access required**
    
    Returns:
        - User ID and username
        - Role
        - Total conversations
        - Total messages
        - Total tokens used
        - Average response time
        - First and last activity timestamps
    """
    return AnalyticsService.get_user_detailed_metrics(db, user_id=user_id, limit=limit)


@router.get("/users/{user_id}/conversations", response_model=List[dict])
async def get_user_conversations(
    user_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of conversations"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for a specific user with metrics.
    
    **Admin access required**
    
    Returns conversation list with:
        - Message count
        - Total tokens
        - Average response time
        - Status and timestamps
    """
    return AnalyticsService.get_conversations_by_user(db, user_id=user_id, limit=limit)


@router.get("/conversations/{conversation_id}/detailed", response_model=dict)
async def get_conversation_detailed(
    conversation_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed metrics for a specific conversation including all messages.
    
    **Admin access required**
    
    Returns:
        - Conversation metadata
        - Token usage
        - Response times
        - Complete message list with individual metrics
    """
    result = AnalyticsService.get_conversation_detailed_metrics(db, conversation_id=conversation_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.get("/tokens/by-conversation", response_model=List[dict])
async def get_token_usage_by_conversation(
    user_id: Optional[str] = Query(None, description="Filter by user"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of conversations"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get token usage breakdown by conversation (sorted by highest usage).
    
    **Admin access required**
    
    Returns:
        - Conversation ID
        - User information
        - Total tokens used
        - Message count
        - Average tokens per message
    """
    return AnalyticsService.get_token_usage_by_conversation(db, user_id=user_id, limit=limit)


@router.get("/response-times/by-user", response_model=List[dict])
async def get_response_times_by_user(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of users"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get response time statistics by user.
    
    **Admin access required**
    
    Returns:
        - User ID and username
        - Average response time
        - Min and max response times
        - Total message count
    """
    return AnalyticsService.get_response_times_by_user(db, limit=limit)


@router.post("/users/sync-profile")
async def sync_user_profile(
    user_id: str,
    username: str,
    role: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to sync user profile from other services.
    
    This should be called when:
    - A new user is created
    - User role is changed
    - User information is updated
    """
    AnalyticsService.sync_user_profile(db, user_id=user_id, username=username, role=role, email=email)
    return {"status": "synced", "user_id": user_id}


@router.delete("/clear-all")
async def clear_all_analytics(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Clear all analytics data from the database.
    
    **Admin access required**
    
    This will delete:
    - All user activities
    - All conversation metrics
    - All message metrics
    - All API usage logs
    - All daily stats
    
    WARNING: This action cannot be undone!
    """
    from analytics.models.analytics import (
        UserActivity, ConversationMetrics, MessageMetrics, 
        APIUsage, DailyStats
    )
    
    # Delete all records from each table
    deleted_counts = {
        "user_activities": db.query(UserActivity).delete(),
        "conversation_metrics": db.query(ConversationMetrics).delete(),
        "message_metrics": db.query(MessageMetrics).delete(),
        "api_usage": db.query(APIUsage).delete(),
        "daily_stats": db.query(DailyStats).delete()
    }
    
    db.commit()
    
    logger.info(f"Admin {current_user.username} cleared all analytics data: {deleted_counts}")
    
    return {
        "message": "All analytics data cleared successfully",
        "deleted_counts": deleted_counts,
        "cleared_by": current_user.username,
        "timestamp": datetime.utcnow().isoformat()
    }


