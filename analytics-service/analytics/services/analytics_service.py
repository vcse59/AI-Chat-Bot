"""Analytics service business logic"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional, List
from analytics.models.analytics import (
    UserActivity, ConversationMetrics, MessageMetrics, 
    APIUsage, SystemMetrics, DailyStats
)
from analytics.schemas.analytics import AnalyticsSummary


class AnalyticsService:
    """Service for analytics operations"""
    
    @staticmethod
    def log_user_activity(
        db: Session,
        user_id: str,
        username: str,
        activity_type: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[dict] = None
    ) -> UserActivity:
        """Log a user activity event"""
        activity = UserActivity(
            user_id=user_id,
            username=username,
            activity_type=activity_type,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def log_api_call(
        db: Session,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> APIUsage:
        """Log an API call"""
        api_usage = APIUsage(
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            status_code=status_code,
            response_time=response_time,
            error_message=error_message
        )
        db.add(api_usage)
        db.commit()
        db.refresh(api_usage)
        return api_usage
    
    @staticmethod
    def get_summary(db: Session) -> AnalyticsSummary:
        """Get overall analytics summary"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count unique users (from both UserActivity and ConversationMetrics)
        total_users_activity = db.query(func.count(func.distinct(UserActivity.user_id))).scalar() or 0
        total_users_conversations = db.query(func.count(func.distinct(ConversationMetrics.user_id))).scalar() or 0
        total_users = max(total_users_activity, total_users_conversations)
        
        # Active users today (users who had activity today)
        active_today = db.query(
            func.count(func.distinct(UserActivity.user_id))
        ).filter(UserActivity.timestamp >= today).scalar() or 0
        
        # Total conversations
        total_conversations = db.query(func.count(ConversationMetrics.id)).scalar() or 0
        
        # Total messages
        total_messages = db.query(func.count(MessageMetrics.id)).scalar() or 0
        
        # Total tokens used
        total_tokens = db.query(func.sum(MessageMetrics.token_count)).scalar() or 0
        
        # Total API calls
        total_api_calls = db.query(func.count(APIUsage.id)).scalar() or 0
        
        # Average response time
        avg_response = db.query(func.avg(APIUsage.response_time)).scalar() or 0.0
        
        # Error rate
        total_calls = db.query(func.count(APIUsage.id)).scalar() or 1
        error_calls = db.query(func.count(APIUsage.id)).filter(
            APIUsage.status_code >= 400
        ).scalar() or 0
        error_rate = (error_calls / total_calls) * 100 if total_calls > 0 else 0.0
        
        return AnalyticsSummary(
            total_users=total_users,
            active_users_today=active_today,
            total_conversations=total_conversations,
            total_messages=total_messages,
            total_tokens=total_tokens,
            total_api_calls=total_api_calls,
            avg_response_time=round(avg_response, 4),
            error_rate=round(error_rate, 2)
        )
    
    @staticmethod
    def get_user_activities(
        db: Session,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[UserActivity]:
        """Get user activities with optional filtering"""
        query = db.query(UserActivity)
        
        if user_id:
            query = query.filter(UserActivity.user_id == user_id)
        if start_date:
            query = query.filter(UserActivity.timestamp >= start_date)
        if end_date:
            query = query.filter(UserActivity.timestamp <= end_date)
        
        return query.order_by(UserActivity.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_conversation_metrics(
        db: Session,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ConversationMetrics]:
        """Get conversation metrics"""
        query = db.query(ConversationMetrics)
        
        if user_id:
            query = query.filter(ConversationMetrics.user_id == user_id)
        
        return query.order_by(ConversationMetrics.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_api_usage_stats(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        endpoint: Optional[str] = None
    ) -> List[APIUsage]:
        """Get API usage statistics"""
        query = db.query(APIUsage)
        
        if start_date:
            query = query.filter(APIUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(APIUsage.timestamp <= end_date)
        if endpoint:
            query = query.filter(APIUsage.endpoint == endpoint)
        
        return query.order_by(APIUsage.timestamp.desc()).limit(1000).all()
    
    @staticmethod
    def get_daily_stats(
        db: Session,
        days: int = 30
    ) -> List[DailyStats]:
        """Get daily statistics for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.query(DailyStats).filter(
            DailyStats.date >= start_date
        ).order_by(DailyStats.date.desc()).all()
    
    @staticmethod
    def get_top_users(
        db: Session,
        limit: int = 10
    ) -> List[dict]:
        """Get top users by activity"""
        results = db.query(
            UserActivity.user_id,
            UserActivity.username,
            func.count(UserActivity.id).label('activity_count')
        ).group_by(
            UserActivity.user_id,
            UserActivity.username
        ).order_by(
            func.count(UserActivity.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "user_id": r.user_id,
                "username": r.username,
                "activity_count": r.activity_count
            }
            for r in results
        ]
