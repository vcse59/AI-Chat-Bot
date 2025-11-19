# Docker Deployment and Validation Guide

## Quick Start

### 1. Setup Environment
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and set:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
AUTH_SECRET_KEY=your-secure-32-char-secret-key-here
```

### 2. Deploy and Validate (One Command)

**Windows:**
```cmd
docker-validate.bat
```

**Linux/Mac:**
```bash
chmod +x docker-validate.sh
./docker-validate.sh
```

This script will:
- ✅ Build all Docker images
- ✅ Start all services
- ✅ Wait for health checks
- ✅ Run validation tests
- ✅ Test MCP integration end-to-end

---

## Manual Deployment Steps

### Step 1: Build Images
```bash
docker-compose build
```

### Step 2: Start Services
```bash
docker-compose up -d
```

### Step 3: Check Status
```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS
auth-server             Up (healthy)
openai-chatbot-api      Up (healthy)
analytics-service       Up (healthy)
chat-frontend           Up
timezone-mcp-server     Up
```

### Step 4: View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f openai-chatbot
docker-compose logs -f timezone-mcp-server
```

---

## Service Endpoints

| Service | Internal URL (Docker) | External URL (Host) |
|---------|----------------------|---------------------|
| Auth Service | http://auth-server:8001 | http://localhost:8001 |
| Chat Service | http://openai-chatbot:8000 | http://localhost:8000 |
| MCP Server | http://timezone-mcp-server:8003 | http://localhost:8003 |
| Frontend | http://chat-frontend:3000 | http://localhost:3000 |
| Analytics | http://analytics-service:8002 | http://localhost:8002 |

---

## Validation Tests

### Quick Validation

**1. Health Checks:**
```bash
curl http://localhost:8001/health  # Auth
curl http://localhost:8000/health  # Chat
curl http://localhost:8003/health  # MCP
```

**2. MCP Tools Endpoint:**
```bash
curl http://localhost:8003/tools | jq
```

Expected:
```json
{
  "tools": [
    {
      "name": "get_current_time",
      "description": "Get current time in a timezone",
      ...
    }
  ]
}
```

### Full Integration Test

**Run pytest suite:**
```bash
cd tests
pytest test_8_mcp_integration.py -v -s
```

### Manual End-to-End Test

**1. Register User:**
```bash
curl -X POST http://localhost:8001/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

**2. Login:**
```bash
TOKEN=$(curl -X POST http://localhost:8001/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test123!" \
  | jq -r .access_token)

echo $TOKEN
```

**3. Register MCP Server:**
```bash
curl -X POST http://localhost:8000/mcp-servers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Timezone MCP Server",
    "description": "Provides timezone information",
    "server_url": "http://timezone-mcp-server:8003",
    "api_key": "'$TOKEN'",
    "is_active": true
  }' | jq
```

**4. Create Conversation:**
```bash
CONV_ID=$(curl -X POST http://localhost:8000/conversations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "MCP Test",
    "system_message": "You are a helpful assistant."
  }' | jq -r .id)

echo $CONV_ID
```

**5. Send Message with MCP Tool:**
```bash
curl -X POST http://localhost:8000/messages/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "'$CONV_ID'",
    "content": "What time is it in Tokyo?"
  }' | jq
```

**Expected Response:**
```json
{
  "user_message": {...},
  "ai_response": {
    "content": "The current time in Tokyo is...",
    "metadata": {
      "mcp_tool_used": true,
      "tool_name": "get_current_time",
      "server_id": "mcp_xxx"
    }
  },
  "response_time_ms": 2500
}
```

---

## Troubleshooting

### Services Not Starting

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**

1. **Port already in use:**
   ```bash
   # Find process using port
   netstat -ano | findstr :8000
   # Kill process or change port in docker-compose.yml
   ```

2. **Build failures:**
   ```bash
   # Clean rebuild
   docker-compose down -v
   docker-compose build --no-cache
   ```

3. **Database issues:**
   ```bash
   # Remove volumes and rebuild
   docker-compose down -v
   docker volume prune
   docker-compose up -d
   ```

### MCP Server Not Responding

**Check MCP server logs:**
```bash
docker-compose logs timezone-mcp-server
```

**Test directly:**
```bash
docker exec -it timezone-mcp-server curl http://localhost:8003/health
```

**Verify network connectivity:**
```bash
# From chat-service container
docker exec -it openai-chatbot-api curl http://timezone-mcp-server:8003/health
```

### OpenAI API Errors

**Check API key:**
```bash
docker exec openai-chatbot-api env | grep OPENAI
```

**Test OpenAI connectivity:**
```bash
docker exec openai-chatbot-api python -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('OpenAI connection OK')
"
```

### MCP Tool Not Being Called

**Debug steps:**

1. **Check MCP server registration:**
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/mcp-servers/
   ```

2. **Verify server is active:**
   - `is_active` should be `true`
   - `server_url` should be `http://timezone-mcp-server:8003`

3. **Check chat-service logs for MCP discovery:**
   ```bash
   docker-compose logs openai-chatbot | grep -i mcp
   ```

4. **Enable debug logging:**
   Edit `docker-compose.yml`:
   ```yaml
   openai-chatbot:
     environment:
       - LOG_LEVEL=DEBUG
   ```

### Database Persistence Issues

**Verify volumes:**
```bash
docker volume ls
docker volume inspect convoai_chatbot_data
```

**Backup database:**
```bash
docker cp openai-chatbot-api:/app/data ./backup
```

---

## Performance Monitoring

### Check Resource Usage
```bash
docker stats
```

### Check Container Health
```bash
docker inspect --format='{{.State.Health.Status}}' auth-server
docker inspect --format='{{.State.Health.Status}}' openai-chatbot-api
```

### View Response Times
```bash
# Enable metrics endpoint (add to docker-compose.yml)
curl http://localhost:8000/metrics
```

---

## Production Deployment

### Security Checklist

- [ ] Change `AUTH_SECRET_KEY` to cryptographically secure value
- [ ] Use environment variables instead of .env file
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure CORS for specific domains
- [ ] Set up database backups
- [ ] Enable log aggregation
- [ ] Configure resource limits in docker-compose.yml
- [ ] Use Docker secrets for sensitive data
- [ ] Enable nginx production profile
- [ ] Set up monitoring and alerting

### Enable Production Mode

```bash
# Start with production profile
docker-compose --profile production up -d
```

### Configure Resource Limits

Edit `docker-compose.yml`:
```yaml
openai-chatbot:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

---

## Cleanup

### Stop Services
```bash
docker-compose down
```

### Remove Volumes (CAUTION: Deletes data)
```bash
docker-compose down -v
```

### Complete Cleanup
```bash
docker-compose down -v --rmi all
docker system prune -a
```

---

## Common Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build openai-chatbot
docker-compose up -d openai-chatbot

# View logs
docker-compose logs -f [service-name]

# Execute command in container
docker-compose exec openai-chatbot bash

# Scale services
docker-compose up -d --scale openai-chatbot=3

# Update service
docker-compose pull
docker-compose up -d

# Export logs
docker-compose logs > logs.txt

# Restart specific service
docker-compose restart openai-chatbot
```

---

## Next Steps

1. ✅ Run validation: `./docker-validate.sh`
2. ✅ Run full tests: `cd tests && pytest test_8_mcp_integration.py -v`
3. ✅ Access frontend: http://localhost:3000
4. ✅ Try the chat with timezone queries
5. ✅ Monitor logs: `docker-compose logs -f`

For detailed MCP integration testing, see: [MCP_INTEGRATION_TEST_GUIDE.md](tests/MCP_INTEGRATION_TEST_GUIDE.md)
