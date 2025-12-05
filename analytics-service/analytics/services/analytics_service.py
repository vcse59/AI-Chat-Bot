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
    def get_user_metrics_by_role(db: Session) -> List[dict]:
        """Get user metrics grouped by role"""
        from analytics.models.analytics import UserProfile, ConversationMetrics, MessageMetrics
        
        # Get metrics for each role
        roles_query = db.query(
            UserProfile.role,
            func.count(func.distinct(UserProfile.user_id)).label('user_count')
        ).group_by(UserProfile.role).all()
        
        results = []
        for role_data in roles_query:
            role = role_data.role or "unknown"
            
            # Get user IDs for this role
            user_ids = [u.user_id for u in db.query(UserProfile.user_id).filter(
                UserProfile.role == role_data.role
            ).all()]
            
            if not user_ids:
                continue
            
            # Get conversation count
            conv_count = db.query(func.count(func.distinct(ConversationMetrics.conversation_id))).filter(
                ConversationMetrics.user_id.in_(user_ids)
            ).scalar() or 0
            
            # Get message count and tokens
            msg_stats = db.query(
                func.count(MessageMetrics.id).label('msg_count'),
                func.sum(MessageMetrics.token_count).label('total_tokens'),
                func.avg(MessageMetrics.response_time).label('avg_response')
            ).filter(MessageMetrics.user_id.in_(user_ids)).first()
            
            results.append({
                "role": role,
                "user_count": role_data.user_count,
                "total_conversations": conv_count,
                "total_messages": msg_stats.msg_count or 0,
                "total_tokens": msg_stats.total_tokens or 0,
                "avg_response_time": round(msg_stats.avg_response or 0.0, 4)
            })
        
        return results
    
    @staticmethod
    def get_user_detailed_metrics(db: Session, user_id: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Get detailed metrics for users"""
        from analytics.models.analytics import UserProfile, ConversationMetrics, MessageMetrics, UserActivity
        
        query = db.query(UserProfile)
        if user_id:
            query = query.filter(UserProfile.user_id == user_id)
        
        # Order by most recent activity and deduplicate by user_id
        users = query.order_by(UserProfile.updated_at.desc()).limit(limit).all()
        
        # Deduplicate by user_id (keep the most recent entry)
        seen_user_ids = set()
        unique_users = []
        for user in users:
            if user.user_id not in seen_user_ids:
                seen_user_ids.add(user.user_id)
                unique_users.append(user)
        
        results = []
        
        for user in unique_users:
            # Get conversation count
            conv_count = db.query(func.count(func.distinct(ConversationMetrics.conversation_id))).filter(
                ConversationMetrics.user_id == user.user_id
            ).scalar() or 0
            
            # Get message stats
            msg_stats = db.query(
                func.count(MessageMetrics.id).label('msg_count'),
                func.sum(MessageMetrics.token_count).label('total_tokens'),
                func.avg(MessageMetrics.response_time).label('avg_response')
            ).filter(MessageMetrics.user_id == user.user_id).first()
            
            # Get activity dates
            first_activity = db.query(func.min(UserActivity.timestamp)).filter(
                UserActivity.user_id == user.user_id
            ).scalar()
            
            last_activity = db.query(func.max(UserActivity.timestamp)).filter(
                UserActivity.user_id == user.user_id
            ).scalar()
            
            results.append({
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role,
                "total_conversations": conv_count,
                "total_messages": msg_stats.msg_count or 0,
                "total_tokens": msg_stats.total_tokens or 0,
                "avg_response_time": round(msg_stats.avg_response or 0.0, 4),
                "first_activity": first_activity,
                "last_activity": last_activity
            })
        
        return results
    
    @staticmethod
    def get_conversations_by_user(db: Session, user_id: str, limit: int = 50) -> List[dict]:
        """Get all conversations for a specific user with detailed metrics"""
        from analytics.models.analytics import ConversationMetrics, UserProfile
        
        conversations = db.query(ConversationMetrics).filter(
            ConversationMetrics.user_id == user_id
        ).order_by(ConversationMetrics.updated_at.desc()).limit(limit).all()
        
        # Get username
        user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        username = user.username if user else None
        
        results = []
        for conv in conversations:
            results.append({
                "conversation_id": conv.conversation_id,
                "user_id": conv.user_id,
                "username": username,
                "message_count": conv.message_count,
                "total_tokens": conv.total_tokens,
                "avg_response_time": round(conv.avg_response_time, 4),
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "status": conv.status
            })
        
        return results
    
    @staticmethod
    def get_conversation_detailed_metrics(db: Session, conversation_id: str) -> dict:
        """Get detailed metrics for a specific conversation including all messages"""
        from analytics.models.analytics import ConversationMetrics, MessageMetrics, UserProfile
        
        conv = db.query(ConversationMetrics).filter(
            ConversationMetrics.conversation_id == conversation_id
        ).first()
        
        if not conv:
            return None
        
        # Get username
        user = db.query(UserProfile).filter(UserProfile.user_id == conv.user_id).first()
        username = user.username if user else None
        
        # Get all messages for this conversation
        messages = db.query(MessageMetrics).filter(
            MessageMetrics.conversation_id == conversation_id
        ).order_by(MessageMetrics.timestamp).all()
        
        message_list = [{
            "message_id": msg.message_id,
            "role": msg.role,
            "token_count": msg.token_count,
            "response_time": msg.response_time,
            "model_used": msg.model_used,
            "timestamp": msg.timestamp
        } for msg in messages]
        
        return {
            "conversation_id": conv.conversation_id,
            "user_id": conv.user_id,
            "username": username,
            "message_count": conv.message_count,
            "total_tokens": conv.total_tokens,
            "avg_response_time": round(conv.avg_response_time, 4),
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "status": conv.status,
            "messages": message_list
        }
    
    @staticmethod
    def get_token_usage_by_conversation(db: Session, user_id: Optional[str] = None, limit: int = 50) -> List[dict]:
        """Get token usage breakdown by conversation"""
        from analytics.models.analytics import ConversationMetrics, UserProfile
        
        query = db.query(ConversationMetrics)
        
        if user_id:
            query = query.filter(ConversationMetrics.user_id == user_id)
        
        conversations = query.order_by(
            ConversationMetrics.total_tokens.desc()
        ).limit(limit).all()
        
        results = []
        for conv in conversations:
            # Get username
            user = db.query(UserProfile).filter(UserProfile.user_id == conv.user_id).first()
            
            results.append({
                "conversation_id": conv.conversation_id,
                "user_id": conv.user_id,
                "username": user.username if user else None,
                "total_tokens": conv.total_tokens,
                "message_count": conv.message_count,
                "avg_tokens_per_message": round(conv.total_tokens / conv.message_count, 2) if conv.message_count > 0 else 0,
                "created_at": conv.created_at
            })
        
        return results
    
    @staticmethod
    def get_response_times_by_user(db: Session, limit: int = 50) -> List[dict]:
        """Get average response times by user"""
        from analytics.models.analytics import MessageMetrics, UserProfile
        
        results = db.query(
            MessageMetrics.user_id,
            func.avg(MessageMetrics.response_time).label('avg_response_time'),
            func.count(MessageMetrics.id).label('message_count'),
            func.min(MessageMetrics.response_time).label('min_response_time'),
            func.max(MessageMetrics.response_time).label('max_response_time')
        ).filter(
            MessageMetrics.response_time.isnot(None)
        ).group_by(
            MessageMetrics.user_id
        ).order_by(
            func.avg(MessageMetrics.response_time).desc()
        ).limit(limit).all()
        
        output = []
        for r in results:
            user = db.query(UserProfile).filter(UserProfile.user_id == r.user_id).first()
            
            output.append({
                "user_id": r.user_id,
                "username": user.username if user else None,
                "avg_response_time": round(r.avg_response_time, 4),
                "min_response_time": round(r.min_response_time, 4),
                "max_response_time": round(r.max_response_time, 4),
                "message_count": r.message_count
            })
        
        return output
    
    @staticmethod
    def sync_user_profile(db: Session, user_id: str, username: str, role: Optional[str] = None, email: Optional[str] = None):
        """Sync or create user profile for analytics tracking"""
        from analytics.models.analytics import UserProfile
        
        user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if user:
            # Update existing
            user.username = username
            if role:
                user.role = role
            if email:
                user.email = email
            user.updated_at = datetime.utcnow()
        else:
            # Create new
            user = UserProfile(
                user_id=user_id,
                username=username,
                role=role,
                email=email
            )
            db.add(user)
        
        db.commit()
        return user
    
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
        
        # Total conversations (all conversations in database)
        total_conversations = db.query(func.count(ConversationMetrics.id)).scalar() or 0
        
        # Active conversations (status = 'active')
        active_conversations = db.query(func.count(ConversationMetrics.id)).filter(
            ConversationMetrics.status == "active"
        ).scalar() or 0
        
        # Total messages (only count assistant messages with tokens - actual OpenAI interactions)
        total_messages = db.query(func.count(MessageMetrics.id)).filter(
            MessageMetrics.role == "assistant",
            MessageMetrics.token_count > 0
        ).scalar() or 0
        
        # Total tokens used (only from assistant messages)
        total_tokens = db.query(func.sum(MessageMetrics.token_count)).filter(
            MessageMetrics.role == "assistant"
        ).scalar() or 0
        
        # Total API calls (excluding analytics service calls to avoid self-tracking)
        total_api_calls = db.query(func.count(APIUsage.id)).filter(
            ~APIUsage.endpoint.like('/api/v1/analytics/%')
        ).scalar() or 0
        
        # Average response time from OpenAI API calls (only messages with response_time)
        avg_response = db.query(func.avg(MessageMetrics.response_time)).filter(
            MessageMetrics.role == "assistant",
            MessageMetrics.response_time.isnot(None)
        ).scalar() or 0.0
        
        # Error rate (excluding analytics service calls)
        total_calls = db.query(func.count(APIUsage.id)).filter(
            ~APIUsage.endpoint.like('/api/v1/analytics/%')
        ).scalar() or 1
        error_calls = db.query(func.count(APIUsage.id)).filter(
            APIUsage.status_code >= 400,
            ~APIUsage.endpoint.like('/api/v1/analytics/%')
        ).scalar() or 0
        error_rate = (error_calls / total_calls) * 100 if total_calls > 0 else 0.0
        
        return AnalyticsSummary(
            total_users=total_users,
            active_users_today=active_today,
            total_conversations=total_conversations,
            active_conversations=active_conversations,
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
