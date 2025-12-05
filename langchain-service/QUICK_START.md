# LangChain Service Quick Start Guide

## 🚀 Running the Service

### Option 1: Standalone (Development)

1. **Navigate to service directory:**
```bash
cd langchain-service
```

2. **Create and activate virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Copy example environment file
copy .env.example .env

# Edit .env and set:
# - OPENAI_API_KEY=your-key-here
# - CHAT_SERVICE_URL=http://localhost:8000
```

5. **Run the service:**
```bash
python main.py
```

Service will be available at: `http://localhost:8004`

### Option 2: Docker

```bash
# Build and run
docker build -t langchain-service .
docker run -p 8004:8004 --env-file .env langchain-service
```

### Option 3: Docker Compose (Recommended)

```bash
# From project root directory
docker-compose up langchain-service

# Or start all services
docker-compose up
```

## 📋 Testing the Service

### 1. Check Health
```bash
curl http://localhost:8004/health
```

### 2. View API Documentation
Open in browser: `http://localhost:8004/docs`

### 3. Start a Conversation
```bash
curl -X POST "http://localhost:8004/api/v1/conversations/start" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "simple_chain",
    "title": "Test Conversation"
  }'
```

### 4. Send a Message
```bash
# Replace {conversation_id} with ID from previous response
curl -X POST "http://localhost:8004/api/v1/conversations/{conversation_id}/message/simple" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Tell me about Python."
  }'
```

## 🔑 Prerequisites

- **Python 3.11+**
- **OpenAI API Key** - Get from https://platform.openai.com/api-keys
- **Chat Service Running** - Service depends on chat-service for message storage

## 🛠️ Configuration

Minimum required environment variables:
```env
OPENAI_API_KEY=sk-...your-key...
CHAT_SERVICE_URL=http://localhost:8000
```

## 📊 Workflow Examples

### Simple Chain (Full Memory)
```python
import requests

base_url = "http://localhost:8004/api/v1"

# Start conversation
resp = requests.post(f"{base_url}/conversations/start", json={
    "workflow_type": "simple_chain"
})
conv_id = resp.json()["id"]

# Chat
resp = requests.post(
    f"{base_url}/conversations/{conv_id}/message/simple",
    json={"message": "What is Python?"}
)
print(resp.json()["ai_response"]["content"])
```

### Structured Chain (Q&A with Context)
```python
resp = requests.post(
    f"{base_url}/conversations/{conv_id}/message/structured",
    json={
        "message": "What are the main features?",
        "chain_type": "qa",
        "context": "Python is a high-level programming language..."
    }
)
```

### Summary Memory (Long Conversations)
```python
resp = requests.post(
    f"{base_url}/conversations/{conv_id}/message/summary-memory",
    json={"message": "Continue our discussion"}
)
```

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check if port 8004 is available
netstat -an | findstr 8004

# Check environment variables
echo %OPENAI_API_KEY%
```

### Chat Service Connection Failed
```bash
# Verify chat-service is running
curl http://localhost:8000/health

# Check CHAT_SERVICE_URL in .env
```

### OpenAI API Errors
- Verify API key is valid
- Check account has credits
- Review rate limits

## 📚 Next Steps

1. **Read Full Documentation**: See [README.md](README.md)
2. **Explore API**: Visit `http://localhost:8004/docs`
3. **Try Different Workflows**: Test simple_chain, structured_chain, summary_memory
4. **Integrate with Frontend**: Connect to your chat application

## 🤝 Integration Points

The service integrates with:
- **Chat Service** (port 8000): Message storage and conversation management
- **Auth Service** (port 8001): User authentication (when using tokens)
- **OpenAI API**: LLM processing via LangChain

## 🎯 Common Use Cases

| Use Case | Endpoint | Workflow |
|----------|----------|----------|
| General chat | `/message/simple` | simple_chain |
| Document Q&A | `/message/structured` | structured (qa) |
| Text summarization | `/message/structured` | structured (summarize) |
| Long conversations | `/message/summary-memory` | summary_memory |

## 📞 Support

For issues:
1. Check logs in terminal/console
2. Review API docs at `/docs`
3. Verify all services are running
4. Check environment configuration
