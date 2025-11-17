# Analytics Integration Guide

## Overview

The ConvoAI platform includes a comprehensive analytics system that tracks user activity, conversation metrics, message statistics, and API usage. This guide explains how to use and understand the analytics features.

## Architecture

### Components

1. **Analytics Service** (Port 8002)
   - Standalone FastAPI service
   - SQLite database for metrics storage
   - Admin-protected API endpoints
   - Public tracking endpoints for service communication

2. **Analytics Middleware**
   - Automatic API request tracking
   - Non-blocking fire-and-forget pattern
   - Integrated into chatbot service

3. **Frontend Analytics Panel**
   - Toggleable side panel in chat interface
   - Real-time metrics display
   - Auto-refresh every 30 seconds

### Data Flow

```
User Action → Frontend → Backend Service
                           ↓
                      Track Event
                           ↓
              Analytics Service (Public Endpoint)
                           ↓
                      Store in DB
                           ↓
              Admin Views Dashboard/Panel
```

## Features

### 1. Analytics Side Panel (Integrated)

**Location**: Chat page header - "📊 Analytics" button (Admin only)

**Features**:
- **Compact Metrics Display**: 6 key metrics in grid layout
  - Total Users
  - Active Users Today
  - Total Conversations
  - Total Messages
  - Total Tokens (OpenAI usage)
  - Average Response Time

- **Recent Activity**: Last 10 user activities
  - Activity type with icon
  - Username
  - Timestamp (relative: "5m ago", "2h ago")

- **Most Active Users**: Top 5 users by activity count
  - Rank badge
  - Username
  - Activity count

- **Auto-refresh**: Updates every 30 seconds
- **Manual Refresh**: Click 🔄 button
- **Toggle**: Click Analytics button to show/hide

### 2. Full Analytics Dashboard

**URL**: `http://localhost:3000/analytics`

**Features**:
- Larger metrics cards with detailed stats
- Extended activity logs (configurable limit)
- User filtering options
- Export capabilities (coming soon)

### 3. API Endpoints

#### Admin Endpoints (Require Admin Token)

**Get Summary**
```bash
GET /api/v1/analytics/summary
Authorization: Bearer <admin_token>
```

**Get User Activities**
```bash
GET /api/v1/analytics/users/activities?limit=50&user_id=user123
Authorization: Bearer <admin_token>
```

**Get Top Users**
```bash
GET /api/v1/analytics/users/top?limit=10
Authorization: Bearer <admin_token>
```

**List Users with Filter**
```bash
GET /api/v1/analytics/users/list?active_only=true
Authorization: Bearer <admin_token>
```

**Get Conversation Metrics**
```bash
GET /api/v1/analytics/conversations?user_id=user123
Authorization: Bearer <admin_token>
```

**Get API Usage Stats**
```bash
GET /api/v1/analytics/api-usage?endpoint=/conversations/
Authorization: Bearer <admin_token>
```

**Get Daily Statistics**
```bash
GET /api/v1/analytics/daily-stats?days=30
Authorization: Bearer <admin_token>
```

#### Public Endpoints (No Auth - Internal Only)

These endpoints are for service-to-service communication within the Docker network:

```bash
POST /api/v1/analytics/track/activity-public
POST /api/v1/analytics/track/api-usage-public
POST /api/v1/analytics/track/conversation-public
POST /api/v1/analytics/track/message-public
```

## Tracked Events

### User Activities
- `login`: User authentication
- `logout`: User sign out
- `conversation_started`: New conversation created
- `conversation_ended`: Conversation deleted
- `message_sent`: User sends message
- `api_call`: General API usage

### Conversation Metrics
- Message count per conversation
- Total tokens used per conversation
- Average response time
- Conversation status (active/deleted)

### Message Metrics
- Individual message details
- Token count per message
- Response time per message
- Model used (e.g., gpt-3.5-turbo)

### API Usage
- Endpoint accessed
- HTTP method
- User ID (if authenticated)
- Status code
- Response time
- Timestamp

## Database Schema

### Analytics Database Tables

**user_activity**
- id (primary key)
- user_id (string)
- username (string)
- activity_type (string)
- timestamp (datetime)
- ip_address (string, optional)
- user_agent (string, optional)
- extra_data (JSON, optional)

**conversation_metrics**
- id (primary key)
- conversation_id (string, unique)
- user_id (string)
- message_count (integer)
- total_tokens (integer)
- avg_response_time (float)
- status (string: active/deleted)
- created_at (datetime)
- updated_at (datetime)

**message_metrics**
- id (primary key)
- message_id (string, unique)
- conversation_id (string)
- user_id (string)
- role (string: user/assistant/system)
- token_count (integer)
- response_time (float, optional)
- model_used (string, optional)
- created_at (datetime)

**api_usage**
- id (primary key)
- endpoint (string)
- method (string)
- user_id (string, optional)
- status_code (integer)
- response_time (float)
- timestamp (datetime)

**daily_stats**
- id (primary key)
- date (date, unique)
- total_users (integer)
- active_users (integer)
- new_users (integer)
- total_conversations (integer)
- total_messages (integer)
- total_api_calls (integer)
- avg_response_time (float)
- error_count (integer)

## Integration Points

### 1. Auth Service Integration

**Location**: `auth-service/auth_server/routers/auth.py`

**Tracked Events**:
- User login → `track_user_activity(activity_type="login")`
- User registration → `track_user_activity(activity_type="registration")`

**Implementation**:
```python
import asyncio
import httpx

async def _track_user_activity(user_id, username, activity_type, ip_address=None, user_agent=None):
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/track/activity-public",
                json={
                    "user_id": user_id,
                    "username": username,
                    "activity_type": activity_type,
                    "ip_address": ip_address,
                    "user_agent": user_agent
                }
            )
    except Exception as e:
        logger.error(f"Failed to track activity: {e}")

# In route handler
asyncio.create_task(_track_user_activity(...))
```

### 2. ChatBot Service Integration

**Location**: `openai_web_service/middleware/analytics_middleware.py`

**Features**:
- Automatic API request tracking
- Helper functions for manual tracking

**Middleware**:
```python
from starlette.middleware.base import BaseHTTPMiddleware

class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        response_time = time.time() - start_time
        
        # Track in background
        asyncio.create_task(self._track_api_usage(...))
        return response
```

**Manual Tracking**:
```python
from middleware.analytics_middleware import track_conversation, track_message

# Track conversation creation
asyncio.create_task(track_conversation(
    conversation_id=conv.id,
    user_id=user.id,
    action="created"
))

# Track message with tokens
asyncio.create_task(track_message(
    message_id=message.id,
    conversation_id=conv.id,
    user_id=user.id,
    role="assistant",
    tokens=150,
    model="gpt-3.5-turbo"
))
```

## Usage Examples

### Admin User Setup

1. Create admin user:
```bash
POST http://localhost:8001/users/
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "secure_password"
}
```

2. Assign admin role (via database):
```sql
INSERT INTO user_roles (user_id, role_id) 
VALUES ('admin_user_id', (SELECT id FROM roles WHERE name='admin'));
```

3. Login as admin:
```bash
POST http://localhost:8001/auth/token
username=admin&password=secure_password
```

### Viewing Analytics

**In-App Side Panel**:
1. Login as admin
2. Click "📊 Analytics" in header
3. Panel slides in from right
4. View metrics and activity

**Full Dashboard**:
1. Navigate to `/analytics`
2. View comprehensive metrics
3. Use filters and exports

**Via API**:
```bash
# Get summary
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/api/v1/analytics/summary

# Get recent activities
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8002/api/v1/analytics/users/activities?limit=20"

# Get active users only
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8002/api/v1/analytics/users/list?active_only=true"
```

## Performance Considerations

### Non-Blocking Tracking

All tracking operations use fire-and-forget pattern:
```python
asyncio.create_task(track_event(...))
```

This ensures:
- User requests are not delayed
- Analytics failures don't affect user experience
- Background processing of metrics

### Auto-Refresh Optimization

Frontend panel uses:
- 30-second refresh interval
- Cancels previous requests on unmount
- Batches multiple API calls with `Promise.all()`

### Database Optimization

- Indexed columns: user_id, conversation_id, timestamp
- Efficient aggregation queries with SQLAlchemy `func`
- Separate database for analytics (no impact on main chat DB)

## Troubleshooting

### Analytics Not Showing Data

**Check Services**:
```bash
docker-compose ps
# Ensure analytics-service is running
```

**Check Admin Role**:
```sql
SELECT u.username, r.name 
FROM users u 
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE u.username = 'your_username';
```

**Check Tracking**:
```bash
# View analytics service logs
docker-compose logs analytics-service -f

# Test tracking endpoint
curl -X POST http://localhost:8002/api/v1/analytics/track/activity-public \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","username":"test","activity_type":"test"}'
```

### Panel Not Loading

1. Clear browser cache
2. Check browser console for errors
3. Verify admin token is valid
4. Check CORS settings

### Slow Performance

1. Reduce auto-refresh interval
2. Limit activity list size
3. Add database indexes
4. Consider pagination for large datasets

## Future Enhancements

- [ ] Export analytics data to CSV/PDF
- [ ] Custom date range filtering
- [ ] Real-time WebSocket updates
- [ ] Advanced charting and visualizations
- [ ] User behavior analysis
- [ ] Conversation quality metrics
- [ ] Cost tracking per user/conversation
- [ ] Alert system for unusual activity
- [ ] A/B testing framework
- [ ] Multi-tenant analytics isolation

## API Reference

For complete API documentation, visit:
- **Analytics Service**: `http://localhost:8002/docs`
- **Auth Service**: `http://localhost:8001/docs`
- **ChatBot Service**: `http://localhost:8000/docs`

## Support

For issues or questions about analytics:
1. Check service health: `http://localhost:8002/health`
2. Review logs: `docker-compose logs analytics-service`
3. Consult main [README.md](README.md)
4. Open GitHub issue with [Analytics] tag
