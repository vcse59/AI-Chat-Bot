"""Middleware to track analytics data"""
import time
import httpx
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import os

logger = logging.getLogger(__name__)

ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8002")


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to track API usage and send to analytics service"""
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get user information if available
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = getattr(request.state.user, 'user_id', None) or getattr(request.state.user, 'username', None)
        
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Track API usage (fire and forget)
        try:
            await self._track_api_usage(
                endpoint=str(request.url.path),
                method=request.method,
                user_id=user_id,
                status_code=response.status_code,
                response_time=response_time
            )
        except Exception as e:
            logger.warning(f"Failed to track analytics: {e}")
        
        return response
    
    async def _track_api_usage(self, endpoint: str, method: str, user_id: str | None, 
                               status_code: int, response_time: float):
        """Send API usage data to analytics service"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/track/api-usage-public",
                    json={
                        "endpoint": endpoint,
                        "method": method,
                        "user_id": user_id,
                        "status_code": status_code,
                        "response_time": response_time
                    }
                )
        except Exception as e:
            logger.debug(f"Analytics tracking failed (non-critical): {e}")


async def track_user_activity(user_id: str, username: str, activity_type: str, 
                              ip_address: str | None = None, user_agent: str | None = None,
                              extra_data: dict | None = None):
    """Track user activity (login, logout, etc.)"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/track/activity-public",
                json={
                    "user_id": user_id,
                    "username": username,
                    "activity_type": activity_type,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "extra_data": extra_data or {}
                }
            )
    except Exception as e:
        logger.debug(f"Activity tracking failed (non-critical): {e}")


async def sync_user_profile(user_id: str, username: str, role: str | None = None, email: str | None = None):
    """Sync user profile with analytics service"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/users/sync-profile",
                params={
                    "user_id": user_id,
                    "username": username,
                    "role": role,
                    "email": email
                }
            )
    except Exception as e:
        logger.debug(f"User profile sync failed (non-critical): {e}")


async def track_conversation(conversation_id: str, user_id: str, action: str):
    """Track conversation creation/deletion"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/track/conversation-public",
                json={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "action": action  # created, deleted, archived
                }
            )
    except Exception as e:
        logger.debug(f"Conversation tracking failed (non-critical): {e}")


async def track_message(message_id: str, conversation_id: str, user_id: str,
                       role: str, token_count: int = 0, response_time: float | None = None,
                       model_used: str | None = None):
    """Track individual message"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/track/message-public",
                json={
                    "message_id": message_id,
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "role": role,
                    "token_count": token_count,
                    "response_time": response_time,
                    "model_used": model_used
                }
            )
    except Exception as e:
        logger.debug(f"Message tracking failed (non-critical): {e}")


async def delete_user_analytics(username: str, auth_token: str):
    """Delete user analytics data from analytics service"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.delete(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/users/{username}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            if response.status_code == 200:
                logger.info(f"Analytics data deleted for user: {username}")
            elif response.status_code == 404:
                logger.debug(f"No analytics data found for user: {username}")
            else:
                logger.warning(f"Failed to delete analytics for user {username}: {response.status_code}")
    except Exception as e:
        logger.warning(f"Analytics deletion failed for user {username}: {e}")
