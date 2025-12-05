# LangChain Workflow Service

A standalone FastAPI-based microservice that provides advanced conversational AI capabilities using LangChain workflows integrated with the ConvoAI platform's chat-service.

## 🎯 Overview

The LangChain Workflow Service is a dedicated microservice that:
- Processes user requests using LangChain's advanced chain-based architecture
- Integrates seamlessly with chat-service for conversation and message management
- Provides multiple workflow types for different use cases
- Leverages OpenAI models through LangChain's abstraction layer

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│         LangChain Workflow Service               │
│              (Port 8004)                         │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────┐     │
│  │      FastAPI Application               │     │
│  │  - RESTful API Endpoints               │     │
│  │  - Authentication Middleware           │     │
│  │  - Error Handling                      │     │
│  └────────────────────────────────────────┘     │
│                    ↓                             │
│  ┌────────────────────────────────────────┐     │
│  │   LangChain Workflow Service           │     │
│  │  - Simple Chain (Buffer Memory)        │     │
│  │  - Structured Chain (Task-Specific)    │     │
│  │  - Summary Memory (Long Conversations) │     │
│  └────────────────────────────────────────┘     │
│                    ↓                             │
│  ┌────────────────────────────────────────┐     │
│  │     Chat Service Client                │     │
│  │  - Conversation Management             │     │
│  │  - Message Persistence                 │     │
│  │  - History Retrieval                   │     │
│  └────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
           ↓                        ↓
┌──────────────────────┐  ┌─────────────────────┐
│   Chat Service       │  │   OpenAI API        │
│   (Port 8000)        │  │   (via LangChain)   │
└──────────────────────┘  └─────────────────────┘
```

## ✨ Features

### 1. **Simple Chain Workflow**
- Full conversation memory with context retention
- Ideal for general chat interactions
- Maintains complete history for context-aware responses

### 2. **Structured Chain Workflow**
- Task-specific chains for specialized operations:
  - **Q&A**: Answer questions with provided context
  - **Summarization**: Summarize long texts
  - **Extraction**: Extract key information
- No memory overhead, optimized for single-turn tasks

### 3. **Summary Memory Workflow**
- Automatic conversation history summarization
- Reduces token usage for long conversations
- Maintains context while optimizing costs

### 4. **Conversation Summaries**
- AI-powered summaries of entire conversations
- Quick overview generation
- Token-efficient for long chat histories

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for Full Platform)

Run with the full ConvoAI platform from project root:

```bash
docker-compose up langchain-service
```

See main [README.md](../README.md) for complete Docker setup.

### Option 2: Standalone Docker Container

**Prerequisites:** Auth service and Chat service should be running.

```bash
# Navigate to langchain-service directory
cd langchain-service

# Copy and configure environment
cp .env.example .env
# Edit .env - set OPENAI_API_KEY, AUTH_SECRET_KEY, service URLs

# Build the Docker image
docker build -t langchain-service .

# Run the container
docker run -d \
  --name langchain-service \
  -p 8004:8004 \
  --env-file .env \
  langchain-service

# Check logs
docker logs -f langchain-service

# Stop the container
docker stop langchain-service
```

**Windows (PowerShell):**
```powershell
# Run the container
docker run -d `
  --name langchain-service `
  -p 8004:8004 `
  --env-file .env `
  langchain-service

# Check logs
docker logs -f langchain-service

# Stop the container
docker stop langchain-service
```

**Windows (Command Prompt):**
```cmd
REM Run the container
docker run -d --name langchain-service -p 8004:8004 --env-file .env langchain-service

REM Check logs
docker logs -f langchain-service

REM Stop the container
docker stop langchain-service
```

### Option 3: Local Development (Without Docker)

**Prerequisites:**
- Python 3.11+
- OpenAI API key
- Auth service running
- Chat service running (optional, for conversation persistence)

**Setup Steps:**

1. **Navigate to service directory:**
   ```bash
   cd langchain-service
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
   
   **Linux/Mac:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```
   
   **Windows (PowerShell):**
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your settings
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   copy .env.example .env
   REM Edit .env with your settings
   ```
   
   **Required settings:**
   - `OPENAI_API_KEY` (required)
   - `AUTH_SECRET_KEY` (must match auth-service)
   - `AUTH_SERVICE_URL=http://localhost:8001`
   - `CHAT_SERVICE_URL=http://localhost:8000`

5. **Run the service:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8004 --reload
   # or
   python main.py
   ```

**Access Points:**
- API: http://localhost:8004
- Swagger Docs: http://localhost:8004/docs
- Health Check: http://localhost:8004/health

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Server
HOST=0.0.0.0
PORT=8004

# Auth service (must match auth-service settings)
AUTH_SERVICE_URL=http://localhost:8001
AUTH_SECRET_KEY=your-secret-key-must-match-auth-service

# Chat service for conversation persistence
CHAT_SERVICE_URL=http://localhost:8000

# LangChain settings
LANGCHAIN_MODEL=gpt-3.5-turbo
LANGCHAIN_TEMPERATURE=0.7
LANGCHAIN_MAX_TOKENS=1000
```

See `.env.example` for full configuration options.

## 📋 API Endpoints

### Start Conversation
```http
POST /api/v1/conversations/start
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "user_id": "user_123",
  "title": "My AI Conversation",
  "system_message": "You are a helpful assistant",
  "workflow_type": "simple_chain"
}
```

**Workflow Types:**
- `simple_chain`: Full memory buffer
- `structured_chain`: Task-specific chains
- `summary_memory`: Summarized history

### Simple Chain Message
```http
POST /api/v1/conversations/{conversation_id}/message/simple
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "message": "Tell me about artificial intelligence",
  "system_prompt": "You are an AI expert"
}
```

### Structured Chain Message
```http
POST /api/v1/conversations/{conversation_id}/message/structured
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "message": "What is the main topic?",
  "chain_type": "qa",
  "context": "Artificial Intelligence is the simulation of human intelligence..."
}
```

**Chain Types:**
- `qa`: Question answering
- `summarize`: Text summarization
- `extract`: Information extraction

### Summary Memory Message
```http
POST /api/v1/conversations/{conversation_id}/message/summary-memory
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "message": "Continue our discussion"
}
```

### Get Conversation Summary
```http
GET /api/v1/conversations/{conversation_id}/summary
Authorization: Bearer YOUR_TOKEN
```

### Clear Conversation Memory
```http
DELETE /api/v1/conversations/{conversation_id}/memory
Authorization: Bearer YOUR_TOKEN
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `CHAT_SERVICE_URL` | Chat service URL | `http://localhost:8000` |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` |
| `LANGCHAIN_MODEL` | OpenAI model | `gpt-3.5-turbo` |
| `LANGCHAIN_TEMPERATURE` | Generation temperature | `0.7` |
| `LANGCHAIN_MAX_TOKENS` | Max tokens per response | `1000` |
| `HOST` | Service host | `0.0.0.0` |
| `PORT` | Service port | `8004` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Model Options
- `gpt-3.5-turbo` (recommended, cost-effective)
- `gpt-4` (more capable, higher cost)
- `gpt-4-turbo` (best performance)

## 📊 Usage Examples

### Python Client Example
```python
import requests

base_url = "http://localhost:8004/api/v1"
token = "your_jwt_token"
headers = {"Authorization": f"Bearer {token}"}

# Start conversation
response = requests.post(
    f"{base_url}/conversations/start",
    json={
        "workflow_type": "simple_chain",
        "title": "Python Discussion"
    },
    headers=headers
)
conversation_id = response.json()["id"]

# Send message
response = requests.post(
    f"{base_url}/conversations/{conversation_id}/message/simple",
    json={"message": "Explain decorators in Python"},
    headers=headers
)
print(response.json()["ai_response"]["content"])

# Get summary
response = requests.get(
    f"{base_url}/conversations/{conversation_id}/summary",
    headers=headers
)
print(response.json()["summary"])
```

### cURL Example
```bash
# Start conversation
curl -X POST http://localhost:8004/api/v1/conversations/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "workflow_type": "simple_chain",
    "title": "Test Conversation"
  }'

# Send message
curl -X POST http://localhost:8004/api/v1/conversations/conv_123/message/simple \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Hello, how are you?"
  }'
```

## 🔗 Integration with Chat Service

The service integrates with chat-service through HTTP API calls:

1. **Conversation Management**: Creates and retrieves conversations via chat-service API
2. **Message Persistence**: Stores all messages in chat-service database
3. **History Retrieval**: Loads conversation history for context
4. **Authentication**: Forwards JWT tokens for user verification

### Integration Flow
```
User Request → LangChain Service → Process with LangChain
                       ↓
            Chat Service Client → Create/Update messages
                       ↓
            Chat Service API → Store in database
                       ↓
            Response ← Return to user
```

## 🏥 Health Check

```bash
curl http://localhost:8004/health
```

Response:
```json
{
  "status": "healthy",
  "service": "langchain-service",
  "version": "1.0.0",
  "chat_service_connected": true,
  "openai_configured": true,
  "timestamp": "2025-11-19T10:00:00"
}
```

## 📚 API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8004/docs`
- ReDoc: `http://localhost:8004/redoc`

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check if OpenAI API key is set
echo %OPENAI_API_KEY%

# Check if chat-service is running
curl http://localhost:8000/health

# Check logs
python main.py
```

### Chat Service Connection Issues
```bash
# Verify CHAT_SERVICE_URL in .env
# Check network connectivity
curl http://localhost:8000/health
```

### OpenAI API Errors
```bash
# Verify API key is valid
# Check OpenAI account credits
# Review rate limits
```

## 🔒 Security

- **Authentication**: JWT tokens forwarded to chat-service
- **Authorization**: Validates user access through chat-service
- **API Key Protection**: OpenAI key stored in environment variables
- **CORS**: Configurable for production deployment

## 🧪 Testing

```bash
# Run manual tests
python -m pytest tests/

# Test specific endpoint
curl http://localhost:8004/health
```

## 📦 Docker Compose Integration

Add to main `docker-compose.yml`:

```yaml
langchain-service:
  build: ./langchain-service
  container_name: langchain-service
  ports:
    - "8004:8004"
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - CHAT_SERVICE_URL=http://chat-service:8000
    - AUTH_SERVICE_URL=http://auth-service:8001
    - LANGCHAIN_MODEL=gpt-3.5-turbo
  depends_on:
    - chat-service
  networks:
    - convoai-network
```

## 🎯 Workflow Selection Guide

| Use Case | Workflow | Reason |
|----------|----------|--------|
| General chat | Simple Chain | Full context retention |
| Q&A with docs | Structured (qa) | Context injection |
| Text summary | Structured (summarize) | Task-specific |
| Long conversations | Summary Memory | Token optimization |
| Quick tasks | Structured | No memory overhead |

## 📈 Performance

- **Average Response Time**: 1-3 seconds
- **Token Usage**: Varies by workflow
  - Simple: Medium (full history)
  - Structured: Low (no memory)
  - Summary: Low (compressed history)
- **Concurrent Requests**: Supports multiple simultaneous requests

## 🤝 Contributing

1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure backwards compatibility

## 📄 License

Part of the ConvoAI platform. See main repository for license information.

## 🆘 Support

For issues or questions:
- Check logs at service startup
- Review API documentation at `/docs`
- Verify environment configuration
- Test chat-service connectivity

## 🔄 Version History

### v1.0.0 (2025-11-19)
- Initial release
- Simple chain workflow
- Structured chain workflow
- Summary memory workflow
- Chat-service integration
- Docker support
