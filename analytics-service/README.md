# Analytics Service

**Admin-Only Analytics and Metrics Tracking for ConvoAI Platform**

## Overview

The Analytics Service is a dedicated microservice that provides comprehensive analytics and metrics tracking for the ConvoAI Platform. This service is **accessible only by users with admin role** and offers insights into:

- User activity and engagement
- Conversation metrics
- Message statistics
- API usage and performance
- System health and errors
- Daily aggregated statistics

## Features

### 🔒 **Admin-Only Access**
- All endpoints require JWT authentication
- Role-based access control (RBAC)
- Only users with `admin` role can access analytics

### 📊 **Comprehensive Metrics**
- **User Analytics**: Track user logins, activities, and top users
- **Conversation Metrics**: Monitor conversation counts, tokens, response times
- **Message Analytics**: Track individual messages, token usage, costs
- **API Usage**: Monitor endpoint performance, error rates, response times
- **Daily Statistics**: Aggregated daily metrics for trend analysis

### 🚀 **Performance Tracking**
- Response time monitoring
- Error rate calculation
- Token usage tracking
- Cost analysis

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for Full Platform)

Run with the full ConvoAI platform from project root:

```bash
docker-compose up analytics-service
```

See main [README.md](../README.md) for complete Docker setup.

### Option 2: Standalone Docker Container

**Prerequisites:** Auth service must be running first.

```bash
# Navigate to analytics-service directory
cd analytics-service

# Copy and configure environment
cp .env.example .env
# Edit .env - set AUTH_SECRET_KEY and AUTH_SERVICE_URL

# Build the Docker image
docker build -t analytics-service .

# Run the container
docker run -d \
  --name analytics-service \
  -p 8002:8002 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  analytics-service

# Check logs
docker logs -f analytics-service

# Stop the container
docker stop analytics-service
```

**Windows (PowerShell):**
```powershell
# Run the container
docker run -d `
  --name analytics-service `
  -p 8002:8002 `
  --env-file .env `
  -v ${PWD}/data:/app/data `
  analytics-service

# Check logs
docker logs -f analytics-service

# Stop the container
docker stop analytics-service
```

**Windows (Command Prompt):**
```cmd
REM Run the container
docker run -d --name analytics-service -p 8002:8002 --env-file .env -v %cd%/data:/app/data analytics-service

REM Check logs
docker logs -f analytics-service

REM Stop the container
docker stop analytics-service
```

### Option 3: Local Development (Without Docker)

**Prerequisites:**
- Python 3.12+
- Auth service running (for authentication)

**Setup Steps:**

1. **Navigate to service directory:**
   ```bash
   cd analytics-service
   ```

2. **Create and activate virtual environment:**
   
   **Windows:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings:
   # - AUTH_SECRET_KEY (must match auth-service)
   # - AUTH_SERVICE_URL=http://localhost:8001
   ```

5. **Create data directory:**
   
   **Linux/Mac:**
   ```bash
   mkdir -p data
   ```
   
   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path data
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   mkdir data 2>nul
   ```

6. **Run the service:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8002 --reload
   ```

**Access Points:**
- API Documentation: http://localhost:8002/docs
- Alternative Docs: http://localhost:8002/redoc
- Health Check: http://localhost:8002/health

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Server
HOST=0.0.0.0
PORT=8002

# Database
DATABASE_URL=sqlite:///./data/analytics.db

# Auth service (must match auth-service settings)
AUTH_SERVICE_URL=http://localhost:8001
AUTH_SECRET_KEY=your-secret-key-must-match-auth-service
```

See `.env.example` for full configuration options.

### Database Configuration

Database is automatically created at `analytics-service/data/analytics.db` using absolute paths. No manual configuration needed.

To reset database:

**Windows:**
```cmd
del analytics-service\data\analytics.db
```

**Linux/Mac:**
```bash
rm analytics-service/data/analytics.db
```

Then restart the service to recreate.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Dashboard                          │
│                  (Future Implementation)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS + Bearer Token (Admin Role)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Analytics Service (Port 8002)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                 │  │
│  │  - Admin-only endpoints                             │  │
│  │  - JWT token validation                             │  │
│  │  - Role checking (require_admin)                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Business Logic Services                            │  │
│  │  - User activity tracking                           │  │
│  │  - Metrics aggregation                              │  │
│  │  - Statistical analysis                             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database Layer (SQLite)                            │  │
│  │  - user_activities                                  │  │
│  │  - conversation_metrics                             │  │
│  │  - message_metrics                                  │  │
│  │  - api_usage                                        │  │
│  │  - system_metrics                                   │  │
│  │  - daily_stats                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Token Verification
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Auth Server (Port 8001)                          │
│            - Validates JWT tokens                           │
│            - Provides user roles                            │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
analytics-service/
├── analytics/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py              # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── analytics.py       # SQLAlchemy models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── analytics.py       # API endpoints (admin-only)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── analytics.py       # Pydantic schemas
│   ├── security/
│   │   ├── __init__.py
│   │   └── auth.py            # JWT validation & RBAC
│   └── services/
│       ├── __init__.py
│       └── analytics_service.py  # Business logic
├── main.py                     # FastAPI application
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Poetry configuration
├── Dockerfile                 # Docker configuration
└── README.md                  # This file
```

## API Endpoints

All endpoints require **admin role** authentication.

### Base URL
```
http://localhost:8002/api/v1/analytics
```

### Authentication
All requests must include a valid JWT token with admin role:
```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### 1. **Get Analytics Summary**
```http
GET /api/v1/analytics/summary
```

Returns overall platform statistics:
- Total users
- Active users today
- Total conversations
- Total messages
- Total API calls
- Average response time
- Error rate

**Example Response:**
```json
{
  "total_users": 150,
  "active_users_today": 42,
  "total_conversations": 1250,
  "total_messages": 8500,
  "total_api_calls": 15000,
  "avg_response_time": 0.2345,
  "error_rate": 2.5
}
```

#### 2. **Get User Activities**
```http
GET /api/v1/analytics/users/activities
```

**Query Parameters:**
- `user_id` (optional): Filter by specific user
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `limit` (default: 100, max: 1000): Number of results

**Example:**
```bash
curl -X GET "http://localhost:8002/api/v1/analytics/users/activities?user_id=user123&limit=50" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 3. **Get Top Users**
```http
GET /api/v1/analytics/users/top
```

Returns most active users by activity count.

**Query Parameters:**
- `limit` (default: 10, max: 100): Number of top users

#### 4. **Get Conversation Metrics**
```http
GET /api/v1/analytics/conversations
```

Returns conversation-level metrics including message counts, tokens, and response times.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `limit` (default: 100, max: 1000): Number of results

#### 5. **Get API Usage Statistics**
```http
GET /api/v1/analytics/api-usage
```

Returns API endpoint usage and performance data.

**Query Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `endpoint` (optional): Filter by specific endpoint

#### 6. **Get Daily Statistics**
```http
GET /api/v1/analytics/daily-stats
```

Returns aggregated daily statistics.

**Query Parameters:**
- `days` (default: 30, max: 365): Number of days to retrieve

#### 7. **Track User Activity** (Manual)
```http
POST /api/v1/analytics/track/activity
```

Manually log a user activity event.

**Request Body:**
```json
{
  "activity_type": "custom_action",
  "metadata": {
    "key": "value"
  }
}
```

## Usage Examples

### Using cURL

#### 1. Get Summary (Admin Token Required)
```bash
# First, login as admin to get token
TOKEN=$(curl -X POST http://localhost:8001/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=adminpass" | jq -r '.access_token')

# Get analytics summary
curl -X GET http://localhost:8002/api/v1/analytics/summary \
  -H "Authorization: Bearer $TOKEN"
```

#### 2. Get User Activities
```bash
curl -X GET "http://localhost:8002/api/v1/analytics/users/activities?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Get Daily Stats
```bash
curl -X GET "http://localhost:8002/api/v1/analytics/daily-stats?days=7" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python

```python
import requests

# Login as admin
auth_response = requests.post(
    "http://localhost:8001/auth/token",
    data={"username": "admin", "password": "adminpass"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
token = auth_response.json()["access_token"]

# Get analytics summary
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8002/api/v1/analytics/summary",
    headers=headers
)
print(response.json())

# Get top users
response = requests.get(
    "http://localhost:8002/api/v1/analytics/users/top?limit=5",
    headers=headers
)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
// Login as admin
const authResponse = await fetch('http://localhost:8001/auth/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: 'username=admin&password=adminpass'
});
const { access_token } = await authResponse.json();

// Get analytics summary
const analyticsResponse = await fetch('http://localhost:8002/api/v1/analytics/summary', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
const analytics = await analyticsResponse.json();
console.log(analytics);
```

## Database Schema

### Tables

#### user_activities
- Tracks user login and activity events
- Fields: user_id, username, activity_type, timestamp, ip_address, user_agent, metadata

#### conversation_metrics
- Conversation-level analytics
- Fields: conversation_id, user_id, message_count, total_tokens, avg_response_time, status

#### message_metrics
- Individual message analytics
- Fields: message_id, conversation_id, role, token_count, response_time, model_used, cost

#### api_usage
- API endpoint usage and performance
- Fields: endpoint, method, user_id, status_code, response_time, error_message

#### system_metrics
- System-wide health metrics
- Fields: metric_name, metric_value, metric_unit, metadata

#### daily_stats
- Aggregated daily statistics
- Fields: date, total_users, active_users, new_users, conversations, messages, tokens, api_calls

## Security

### Authentication
- JWT token validation
- Token must be obtained from auth-server (port 8001)
- Token includes user roles

### Authorization
- All analytics endpoints require admin role
- `require_admin` dependency checks user roles
- Non-admin users receive 403 Forbidden

### Best Practices
- Never expose analytics endpoints publicly
- Use HTTPS in production
- Rotate admin credentials regularly
- Monitor analytics access logs
- Set appropriate token expiration times

## Running the Service

### With Docker Compose (Recommended)
```bash
# Build and start all services including analytics
docker-compose up --build

# Analytics service will be available at http://localhost:8002
```

### Standalone (Development)
```bash
cd analytics-service

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AUTH_SECRET_KEY="your-secret-key"
export AUTH_SERVICE_URL="http://localhost:8001"

# Run the service
uvicorn main:app --reload --port 8002
```

### Using Poetry
```bash
cd analytics-service
poetry install
poetry run uvicorn main:app --reload --port 8002
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | 8002 |
| `HOST` | Service host | 0.0.0.0 |
| `AUTH_SECRET_KEY` | JWT secret key (shared with auth-server) | Required |
| `AUTH_SERVICE_URL` | Auth server URL | http://auth-server:8001 |
| `CORS_ORIGINS` | Allowed CORS origins | * |

## Health Check

```bash
curl http://localhost:8002/health
```

Response:
```json
{
  "status": "healthy",
  "service": "analytics-service",
  "version": "1.0.0"
}
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Creating an Admin User

To access the analytics service, you need an admin user:

```bash
# Using the auth-server API
curl -X POST http://localhost:8001/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure_admin_password",
    "full_name": "System Administrator"
  }'

# Then assign admin role (requires existing admin access or direct DB modification)
```

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Analytics service only
docker-compose logs -f analytics-service
```

### Check Service Status
```bash
docker-compose ps
```

## Future Enhancements

- [ ] Real-time analytics dashboard (React/Vue frontend)
- [ ] Export analytics to CSV/Excel
- [ ] Scheduled reports via email
- [ ] Advanced data visualizations (charts, graphs)
- [ ] Machine learning insights
- [ ] Anomaly detection
- [ ] Cost optimization recommendations
- [ ] Integration with external analytics platforms
- [ ] Multi-tenancy support
- [ ] Advanced filtering and search

## Troubleshooting

### Analytics Service Not Starting
1. Check if auth-server is running
2. Verify AUTH_SECRET_KEY matches across services
3. Check logs: `docker-compose logs analytics-service`

### 401 Unauthorized Error
- Ensure token is valid and not expired
- Verify token includes user roles
- Check AUTH_SECRET_KEY configuration

### 403 Forbidden Error
- User does not have admin role
- Verify user roles in auth-server database
- Ensure JWT token includes roles claim

### Database Issues
- Check if volume is mounted correctly
- Verify write permissions
- Database is automatically created on first run

## Contributing

When adding new analytics features:
1. Add model to `analytics/models/analytics.py`
2. Create schema in `analytics/schemas/analytics.py`
3. Implement service logic in `analytics/services/analytics_service.py`
4. Add endpoint in `analytics/routers/analytics.py`
5. Ensure admin-only access with `require_admin` dependency
6. Update this README with new endpoints

## License

Part of the AI Chat Bot Platform - See main project LICENSE

## Support

For issues and questions:
- Check logs: `docker-compose logs analytics-service`
- Review API docs: http://localhost:8002/docs
- Verify admin role assignment
- Check auth-server connectivity

---

**Built with ❤️ for Admin Analytics**
