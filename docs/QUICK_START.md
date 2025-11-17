# Quick Start Guide - ConvoAI System

## 🚀 Current Status: All Systems Operational

### Running Services (4/4)
- ✅ **Auth Server** - Port 8001 (Healthy)
- ✅ **OpenAI ChatBot API** - Port 8000 (Healthy)
- ✅ **Analytics Service** - Port 8002 (Healthy) ⭐ NEW
- ✅ **Chat Frontend** - Port 3000 (Running)

## Quick Commands

### Start All Services
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f analytics-service
docker-compose logs -f auth-server
docker-compose logs -f openai-chatbot
docker-compose logs -f chat-frontend
```

### Check Service Status
```bash
docker-compose ps
```

### Restart a Service
```bash
docker-compose restart analytics-service
```

### Rebuild a Service
```bash
docker-compose up -d --build analytics-service
```

## Access Points

| Service | URL | API Docs | Purpose |
|---------|-----|----------|---------|
| **Auth** | http://localhost:8001 | http://localhost:8001/docs | User authentication & authorization |
| **ChatBot** | http://localhost:8000 | http://localhost:8000/docs | OpenAI chat API & WebSocket |
| **Analytics** | http://localhost:8002 | http://localhost:8002/docs | Admin-only analytics & metrics ⭐ |
| **Frontend** | http://localhost:3000 | N/A | React web interface |

## Testing the System

### 1. Test Health Endpoints
```bash
curl http://localhost:8001/health
curl http://localhost:8000/health
curl http://localhost:8002/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "analytics-service",
  "version": "1.0.0"
}
```

### 2. Create a User Account
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'
```

### 3. Login and Get Token
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

Response will contain `access_token` - save this for authenticated requests.

### 4. Test Analytics Service (Admin Only)
```bash
# This will return 403 Forbidden if user is not admin
curl -X GET http://localhost:8002/api/v1/analytics/summary \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Analytics API Endpoints ⭐ NEW

All endpoints require **admin role** authentication.

### GET /api/v1/analytics/summary
Overall analytics summary with counts and statistics.

### GET /api/v1/analytics/users/activities
List all user activity logs with pagination.
- Query params: `skip=0`, `limit=50`

### GET /api/v1/analytics/users/top
Get most active users.
- Query params: `limit=10`

### GET /api/v1/analytics/conversations
Conversation metrics with optional date filtering.
- Query params: `start_date`, `end_date`, `user_id`

### GET /api/v1/analytics/api-usage
API endpoint performance metrics.
- Query params: `start_date`, `end_date`, `endpoint`

### GET /api/v1/analytics/daily-stats
Aggregated daily statistics.
- Query params: `start_date`, `end_date`

### POST /api/v1/analytics/track/activity
Manually log a user activity.
```json
{
  "user_id": "string",
  "username": "string",
  "activity_type": "login",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "extra_data": {"key": "value"}
}
```

## Environment Variables

Create or edit `.env` file:
```env
# Shared secret for JWT authentication (CHANGE THIS!)
AUTH_SECRET_KEY=your-secret-key-here-change-in-production

# OpenAI API Key (required for chat functionality)
OPENAI_API_KEY=your-api-key-here
```

## Database Locations

All databases are stored in Docker named volumes:
- **auth_data**: `/var/lib/docker/volumes/open-chatbot_auth_data/_data`
- **chatbot_data**: `/var/lib/docker/volumes/open-chatbot_chatbot_data/_data`
- **analytics_data**: `/var/lib/docker/volumes/open-chatbot_analytics_data/_data` ⭐

### View Volume Data
```bash
# List volumes
docker volume ls

# Inspect a volume
docker volume inspect open-chatbot_analytics_data

# Access volume data (Linux/Mac)
sudo ls /var/lib/docker/volumes/open-chatbot_analytics_data/_data

# Windows (WSL2)
\\wsl$\docker-desktop-data\data\docker\volumes\open-chatbot_analytics_data\_data
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs servicename

# Rebuild from scratch
docker-compose build --no-cache servicename
docker-compose up -d servicename
```

### Database Issues
```bash
# Remove and recreate volume
docker-compose down servicename
docker volume rm open-chatbot_analytics_data
docker-compose up -d servicename
```

### Port Conflicts
If ports are already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8002:8002"  # Change left side: "8003:8002"
```

### Reset Everything
```bash
# WARNING: This will delete all data!
docker-compose down -v
docker-compose up -d
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   chat-frontend                     │
│                   React App :3000                   │
└───────┬─────────────┬─────────────┬─────────────────┘
        │             │             │
   ┌────▼────┐   ┌────▼────┐   ┌────▼──────┐
   │  Auth   │   │ChatBot  │   │Analytics  │
   │ :8001   │◄──│ :8000   │   │ :8002     │
   │ JWT+RBAC│   │WS+API   │   │Admin Only │
   └────┬────┘   └────┬────┘   └────┬──────┘
        │             │             │
   ┌────▼────┐   ┌────▼────┐   ┌────▼──────┐
   │auth_data│   │chatbot  │   │analytics  │
   │ SQLite  │   │_data    │   │_data      │
   │         │   │SQLite   │   │SQLite     │
   └─────────┘   └─────────┘   └───────────┘
```

## What's New in Analytics Service ⭐

- **Admin-Only Access**: All endpoints require admin role
- **6 Database Models**: 
  - UserActivity (logins, logouts, API calls)
  - ConversationMetrics (message counts, tokens, response times)
  - MessageMetrics (per-message statistics)
  - APIUsage (endpoint performance)
  - SystemMetrics (system health)
  - DailyStats (aggregated reports)
- **8 API Endpoints**: Complete analytics REST API
- **JWT Integration**: Uses shared AUTH_SECRET_KEY
- **Auto Health Checks**: Monitored by Docker

## Production Deployment

Before deploying to production:

1. **Change Secret Keys**
   ```env
   AUTH_SECRET_KEY=<generate-strong-random-key>
   ```

2. **Secure OpenAI Key**
   ```env
   OPENAI_API_KEY=<your-actual-openai-key>
   ```

3. **Enable HTTPS**
   - Uncomment nginx service in `docker-compose.yml`
   - Add SSL certificates
   - Update frontend environment variables

4. **Database Backups**
   ```bash
   docker run --rm -v open-chatbot_analytics_data:/data \
     -v $(pwd):/backup alpine \
     tar czf /backup/analytics-backup.tar.gz -C /data .
   ```

5. **Resource Limits**
   Add to `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

## Support

For issues or questions:
1. Check logs: `docker-compose logs servicename`
2. Review `DEPLOYMENT_STATUS.md` for detailed information
3. Check API docs: http://localhost:8002/docs
4. Verify `.env` file configuration

## Next Steps

1. ✅ Create admin user account
2. ✅ Test analytics endpoints with admin token
3. ⏳ Implement automatic activity tracking in chatbot service
4. ⏳ Build analytics dashboard in frontend
5. ⏳ Configure monitoring and alerts
6. ⏳ Set up production deployment with HTTPS
