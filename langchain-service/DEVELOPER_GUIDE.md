# LangChain Service - Developer Documentation

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Decisions](#design-decisions)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [API Design](#api-design)
6. [Integration Patterns](#integration-patterns)
7. [Memory Management](#memory-management)
8. [Error Handling](#error-handling)
9. [Security Considerations](#security-considerations)
10. [Performance Optimization](#performance-optimization)
11. [Testing Strategy](#testing-strategy)
12. [Deployment Guide](#deployment-guide)
13. [Troubleshooting](#troubleshooting)
14. [Contributing Guidelines](#contributing-guidelines)

---

## 🏗️ Architecture Overview

### System Context

```
┌─────────────────────────────────────────────────────────┐
│                   ConvoAI Platform                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Auth Service │  │ Chat Service │  │   Analytics  │ │
│  │  (Port 8001) │  │ (Port 8000)  │  │ (Port 8002)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                            │
│         └──────────┬───────┘                            │
│                    │                                    │
│         ┌──────────▼──────────┐                        │
│         │  LangChain Service  │                        │
│         │    (Port 8004)      │◄───────────────────────┤
│         └─────────────────────┘      User Requests    │
│                    │                                    │
│                    ▼                                    │
│         ┌─────────────────────┐                        │
│         │    OpenAI API       │                        │
│         │  (via LangChain)    │                        │
│         └─────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

### Microservice Architecture

The LangChain service follows a **microservice architecture pattern** with:

- **Independence**: Can be deployed, scaled, and maintained separately
- **Single Responsibility**: Handles only LangChain workflow processing
- **API-First Design**: RESTful API for all interactions
- **Stateless**: Application logic is stateless (memory cached in-process)
- **Async Operations**: Full async/await for non-blocking I/O

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Framework** | FastAPI | Modern, async, auto-documented API |
| **AI Framework** | LangChain | Chain-based AI workflow orchestration |
| **LLM Provider** | OpenAI (via LangChain) | Language model processing |
| **HTTP Client** | HTTPX | Async HTTP for service integration |
| **Validation** | Pydantic | Data validation and settings |
| **Logging** | Python JSON Logger | Structured logging |
| **Container** | Docker | Containerization |
| **Orchestration** | Docker Compose | Multi-service orchestration |

---

## 🎯 Design Decisions

### 1. Separate Service vs. Integration

**Decision**: Create a separate microservice instead of integrating into chat-service

**Rationale**:
- **Separation of Concerns**: LangChain logic isolated from core chat functionality
- **Independent Scaling**: Can scale LangChain processing independently
- **Technology Freedom**: Can use different dependencies without conflicts
- **Deployment Flexibility**: Can deploy/update without affecting chat-service
- **Resource Management**: LangChain memory management separate from chat-service
- **Testing**: Easier to test in isolation

**Trade-offs**:
- ✅ Better modularity and maintainability
- ✅ Independent deployment cycles
- ✅ Clearer service boundaries
- ⚠️ Additional network latency (minimal with Docker networking)
- ⚠️ More services to manage (mitigated by docker-compose)

### 2. Chat-Service Integration Pattern

**Decision**: Use HTTP client to integrate with chat-service API

**Rationale**:
- **Leverage Existing Infrastructure**: Reuse chat-service's conversation/message management
- **Single Source of Truth**: All messages stored in chat-service database
- **Consistency**: Same data model across services
- **Authentication**: Reuse existing auth mechanisms
- **No Database Duplication**: Avoid data synchronization issues

**Implementation**:
```python
class ChatServiceClient:
    """HTTP client for chat-service integration"""
    
    async def create_conversation(self, user_id, title, metadata)
    async def get_conversation_messages(self, conversation_id, limit)
    async def create_message(self, conversation_id, content, role, metadata)
```

### 3. Memory Management Strategy

**Decision**: In-memory caching with manual clear option

**Rationale**:
- **Performance**: Fast access without database queries
- **LangChain Pattern**: Follows LangChain's memory abstractions
- **Flexibility**: Users can clear memory without deleting messages
- **Stateless Restarts**: Fresh memory on service restart (by design)

**Alternative Considered**: Redis-backed memory
- **Future Enhancement**: Can add Redis persistence layer later
- **Current**: Simpler for initial implementation

### 4. Three Workflow Types

**Decision**: Implement three distinct workflow patterns

**Rationale**:
- **Use Case Coverage**: Different needs require different approaches
  - **Simple Chain**: General conversation with full context
  - **Structured Chain**: Task-specific processing (Q&A, summarization)
  - **Summary Memory**: Long conversations with token optimization
- **User Choice**: Let users select optimal workflow for their needs
- **Token Optimization**: Different strategies for different conversation lengths
- **Flexibility**: Easy to add more workflows later

### 5. Async Architecture

**Decision**: Full async/await implementation

**Rationale**:
- **Non-blocking I/O**: Handle multiple requests concurrently
- **OpenAI API Calls**: Long-running operations don't block
- **HTTP Requests**: Async calls to chat-service
- **FastAPI Native**: FastAPI is async-first
- **Scalability**: Better resource utilization

### 6. Type Safety with Pydantic

**Decision**: Complete type hints and Pydantic models

**Rationale**:
- **Runtime Validation**: Catch errors early
- **Auto-documentation**: FastAPI generates docs from types
- **IDE Support**: Better autocomplete and error detection
- **Self-documenting**: Types serve as documentation
- **Data Integrity**: Ensures correct data shapes

---

## 🔧 Component Details

### 1. FastAPI Application (`app/main.py`)

**Purpose**: Main application entry point and configuration

**Key Components**:
```python
app = FastAPI(
    title="LangChain Workflow Service",
    description="Advanced AI conversation workflows",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc"     # ReDoc alternative
)
```

**Middleware**:
- **CORS**: Cross-origin resource sharing
- **Error Handling**: Global exception handlers (can be added)
- **Logging**: Request/response logging (can be added)

**Lifecycle Events**:
```python
@app.on_event("startup")
async def startup_event():
    # Initialize resources
    # Log startup information
    
@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources
    # Close connections
```

### 2. API Routes (`app/api/routes.py`)

**Purpose**: Define HTTP endpoints and request handling

**Route Pattern**:
```python
@router.post("/conversations/{conversation_id}/message/simple")
async def send_message_simple_chain(
    conversation_id: str,                               # Path parameter
    request: MessageRequest,                             # Request body
    service: LangChainWorkflowService = Depends(...)    # Dependency injection
) -> WorkflowResponse:                                  # Response model
    # Handle request
    # Return response
```

**Dependency Injection**:
```python
async def get_workflow_service(
    authorization: Optional[str] = Header(None)
) -> LangChainWorkflowService:
    """
    Creates service instance with auth token
    Automatically closed after request
    """
    token = extract_token(authorization)
    service = LangChainWorkflowService(token=token)
    try:
        yield service
    finally:
        await service.close()
```

**Benefits**:
- Automatic token extraction
- Service lifecycle management
- Resource cleanup guaranteed
- Testable (can mock dependencies)

### 3. LangChain Workflow Service (`app/services/langchain_workflow.py`)

**Purpose**: Core business logic for LangChain processing

**Class Structure**:
```python
class LangChainWorkflowService:
    def __init__(self, token: str = None):
        self.chat_client = ChatServiceClient(token=token)
        self.llm = ChatOpenAI(...)
        self._conversation_memories: Dict[str, Memory] = {}
    
    # Conversation Management
    async def start_conversation(...)
    
    # Workflow Processing
    async def process_simple_chain(...)
    async def process_structured_chain(...)
    async def process_summary_memory(...)
    
    # Utilities
    async def get_conversation_summary(...)
    async def _get_or_create_memory(...)
    def clear_conversation_memory(...)
```

**Key Responsibilities**:
1. LangChain chain creation and execution
2. Memory management (buffer, summary)
3. Chat-service integration
4. Token tracking
5. Response time measurement

### 4. Chat Service Client (`app/services/chat_service_client.py`)

**Purpose**: HTTP client for chat-service API integration

**Methods**:
```python
class ChatServiceClient:
    async def create_conversation(...)     # POST /users/{id}/conversations/
    async def get_conversation(...)        # GET /conversations/{id}
    async def get_conversation_messages(...)  # GET /conversations/{id}/messages/
    async def create_message(...)          # POST /conversations/{id}/messages/
    async def health_check(...)            # GET /health
```

**Error Handling**:
```python
try:
    response = await self.client.post(url, json=payload)
    response.raise_for_status()
    return response.json()
except httpx.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### 5. Configuration Management (`app/utils/config.py`)

**Purpose**: Centralized configuration using Pydantic Settings

**Implementation**:
```python
class Settings(BaseSettings):
    # Service Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    
    # Required
    OPENAI_API_KEY: str
    
    # Service URLs
    CHAT_SERVICE_URL: str = "http://localhost:8000"
    
    # LangChain Config
    LANGCHAIN_MODEL: str = "gpt-3.5-turbo"
    LANGCHAIN_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**Benefits**:
- Type validation at startup
- Environment variable loading
- Default values
- Cached instance (singleton pattern)
- IDE autocomplete

### 6. Pydantic Models (`app/models/schemas.py`)

**Purpose**: Request/response validation and documentation

**Examples**:
```python
class MessageRequest(BaseModel):
    """Request to send a message"""
    message: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None

class WorkflowResponse(BaseModel):
    """Response from workflow processing"""
    conversation_id: str
    user_message: Dict[str, Any]
    ai_response: Dict[str, Any]
    response_time_ms: int
    tokens_used: Optional[int]
    workflow_type: str
```

**Features**:
- Automatic validation
- JSON schema generation
- OpenAPI documentation
- Type conversion
- Custom validators

---

## 📊 Data Flow

### Complete Request Flow

```
1. User Request
   ↓
2. FastAPI Router
   ↓
3. Dependency Injection
   └─→ Create LangChainWorkflowService
       └─→ Extract auth token
   ↓
4. Request Validation (Pydantic)
   ↓
5. LangChain Workflow Service
   ├─→ Load/Create Memory
   │   └─→ Fetch messages from chat-service
   ├─→ Build LangChain Chains
   ├─→ Execute with OpenAI
   └─→ Track tokens/timing
   ↓
6. Chat Service Client
   ├─→ Save user message
   └─→ Save AI response
   ↓
7. Response Serialization
   ↓
8. HTTP Response to User
```

### Simple Chain Flow (Detailed)

```python
# 1. Request arrives
POST /api/v1/conversations/conv_123/message/simple
{
  "message": "Tell me about Python",
  "system_prompt": "You are a programming expert"
}

# 2. Dependency injection creates service
service = LangChainWorkflowService(token=user_token)

# 3. Load conversation memory
memory = await service._get_or_create_memory(conv_id)
# → Fetches messages from chat-service
# → Populates LangChain memory

# 4. Build conversation chain
prompt = ChatPromptTemplate.from_messages([
    SystemMessage("You are a programming expert"),
    MessagesPlaceholder("history"),  # Loaded messages
    HumanMessage("{input}")
])
chain = ConversationChain(llm=llm, memory=memory, prompt=prompt)

# 5. Execute chain with token tracking
with get_openai_callback() as cb:
    response = await chain.apredict(input="Tell me about Python")
    tokens_used = cb.total_tokens

# 6. Save messages to chat-service
user_msg = await chat_client.create_message(
    conversation_id=conv_id,
    content="Tell me about Python",
    role="user"
)
ai_msg = await chat_client.create_message(
    conversation_id=conv_id,
    content=response,
    role="assistant",
    metadata={"tokens_used": tokens_used}
)

# 7. Return response
return {
    "conversation_id": conv_id,
    "user_message": user_msg,
    "ai_response": ai_msg,
    "tokens_used": tokens_used,
    "workflow_type": "simple_chain"
}
```

### Structured Chain Flow (Q&A Example)

```python
# 1. Request with context
POST /api/v1/conversations/conv_123/message/structured
{
  "message": "What is the capital?",
  "chain_type": "qa",
  "context": "France is a country in Europe..."
}

# 2. Build Q&A-specific prompt
prompt = ChatPromptTemplate.from_messages([
    SystemMessage("""Answer questions based on context.
    Context: {context}"""),
    HumanMessage("{input}")
])

# 3. Create LLMChain (no memory)
chain = LLMChain(llm=llm, prompt=prompt)

# 4. Execute with context injection
response = await chain.apredict(
    input="What is the capital?",
    context="France is a country in Europe..."
)

# 5. Save messages (same as simple chain)
# 6. Return response with chain_type metadata
```

---

## 🔐 Security Considerations

### 1. API Key Protection

**OpenAI API Key**:
- ✅ Stored in environment variables (not in code)
- ✅ Not exposed in API responses
- ✅ Not logged in application logs
- ✅ Docker secrets recommended for production

### 2. Authentication Flow

```
User Request with JWT Token
   ↓
LangChain Service
   ├─→ Extracts token from Authorization header
   └─→ Forwards to chat-service
       ↓
   Chat Service
       ├─→ Validates JWT with auth-service
       └─→ Returns 401 if invalid
```

**Current Implementation**:
```python
async def get_workflow_service(
    authorization: Optional[str] = Header(None)
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    service = LangChainWorkflowService(token=token)
    # Token forwarded to chat-service in all requests
```

### 3. Input Validation

**Pydantic Models**:
```python
class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    system_prompt: Optional[str] = Field(None, max_length=1000)
    
    @validator('message')
    def validate_message(cls, v):
        # Custom validation logic
        return v.strip()
```

### 4. Rate Limiting (Future Enhancement)

```python
# Can add rate limiting middleware
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/conversations/{id}/message/simple")
@limiter.limit("10/minute")
async def send_message(...):
    pass
```

### 5. CORS Configuration

**Development**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## ⚡ Performance Optimization

### 1. Async/Await Pattern

**All I/O Operations are Async**:
```python
# ✅ Good - Non-blocking
async def process_message():
    messages = await chat_client.get_messages()  # Async HTTP
    response = await chain.apredict(input)        # Async OpenAI
    await chat_client.save_message()              # Async HTTP

# ❌ Bad - Blocking
def process_message():
    messages = chat_client.get_messages_sync()    # Blocks event loop
    response = chain.predict_sync(input)           # Blocks event loop
```

### 2. Memory Caching

**In-Memory Storage**:
```python
# Cache conversation memories
self._conversation_memories: Dict[str, ConversationBufferMemory] = {}

# Reuse memory for same conversation
if conversation_id in self._conversation_memories:
    return self._conversation_memories[conversation_id]
```

**Benefits**:
- Avoid repeated database queries
- Faster memory access
- Reduced latency

**Considerations**:
- Memory grows with active conversations
- Cleared on service restart
- Can add TTL expiration (future)

### 3. HTTP Connection Pooling

**HTTPX Client**:
```python
self.client = httpx.AsyncClient(
    timeout=60.0,
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100
    )
)
```

**Benefits**:
- Reuse TCP connections
- Reduce connection overhead
- Better throughput

### 4. Token Usage Optimization

**Workflow Selection Guide**:
| Conversation Length | Recommended | Token Efficiency |
|---------------------|-------------|------------------|
| 1-10 messages | Simple Chain | Medium |
| 10-50 messages | Simple Chain | Medium |
| 50+ messages | Summary Memory | High |
| One-off tasks | Structured Chain | Highest |

**Summary Memory Benefits**:
- Compresses old messages into summary
- Maintains context with fewer tokens
- Significant cost savings for long conversations

### 5. Response Streaming (Future Enhancement)

```python
# Current: Wait for complete response
response = await chain.apredict(input)

# Future: Stream tokens as they arrive
async for token in chain.astream(input):
    yield token
```

---

## 🧪 Testing Strategy

### 1. Unit Tests

**Test Each Component Independently**:

```python
# Test LangChain workflow service
def test_create_simple_chain():
    service = LangChainWorkflowService()
    chain = service._create_simple_chain(prompt="Test")
    assert chain is not None
    assert isinstance(chain, ConversationChain)

# Test chat service client
@pytest.mark.asyncio
async def test_create_conversation():
    client = ChatServiceClient()
    with pytest.raises(httpx.HTTPError):
        await client.create_conversation("test_user", "Test")
```

### 2. Integration Tests

**Test Service Integration**:

```python
@pytest.mark.asyncio
async def test_end_to_end_workflow():
    # Mock chat-service responses
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "id": "conv_123",
            "user_id": "user_1"
        }
        
        service = LangChainWorkflowService()
        result = await service.start_conversation("user_1")
        
        assert result["id"] == "conv_123"
        mock_post.assert_called_once()
```

### 3. API Tests

**Test HTTP Endpoints**:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_start_conversation():
    response = client.post(
        "/api/v1/conversations/start",
        json={"workflow_type": "simple_chain"}
    )
    assert response.status_code == 200
```

### 4. Mock OpenAI Responses

**Avoid Real API Calls in Tests**:

```python
@patch('langchain_openai.ChatOpenAI')
def test_process_message(mock_llm):
    mock_llm.return_value.apredict.return_value = "Test response"
    
    service = LangChainWorkflowService()
    result = await service.process_simple_chain(...)
    
    assert result["ai_response"]["content"] == "Test response"
```

### 5. Load Testing

**Performance Testing**:

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8004/health

# Using Locust
locust -f load_test.py --host=http://localhost:8004
```

---

## 🚀 Deployment Guide

### Development Environment

```bash
# 1. Clone repository
cd langchain-service

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run service
python main.py

# Service available at http://localhost:8004
```

### Docker Deployment

```bash
# Build image
docker build -t langchain-service:latest .

# Run container
docker run -d \
  --name langchain-service \
  -p 8004:8004 \
  --env-file .env \
  langchain-service:latest

# Check logs
docker logs -f langchain-service

# Stop container
docker stop langchain-service
```

### Docker Compose Deployment

```yaml
# docker-compose.yml
langchain-service:
  build: ./langchain-service
  container_name: langchain-service
  ports:
    - "8004:8004"
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - CHAT_SERVICE_URL=http://chat-service:8000
  depends_on:
    - chat-service
  networks:
    - convoai-network
```

```bash
# Start all services
docker-compose up -d

# Start only langchain-service
docker-compose up -d langchain-service

# View logs
docker-compose logs -f langchain-service

# Rebuild and restart
docker-compose up -d --build langchain-service
```

### Production Deployment

**Environment Configuration**:
```bash
# Use production OpenAI key
OPENAI_API_KEY=sk-prod-...

# Use production service URLs
CHAT_SERVICE_URL=https://chat.yourdomain.com
AUTH_SERVICE_URL=https://auth.yourdomain.com

# Optimize settings
LANGCHAIN_VERBOSE=false
LOG_LEVEL=WARNING
```

**Docker Optimization**:
```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "main.py"]
```

**Health Checks**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8004/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Error**: `ModuleNotFoundError: No module named 'langchain'`

**Solution**:
```bash
pip install -r requirements.txt
```

#### 2. OpenAI API Key Error

**Error**: `openai.error.AuthenticationError: Incorrect API key`

**Solution**:
```bash
# Check if key is set
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows

# Set in .env file
OPENAI_API_KEY=sk-...your-key...
```

#### 3. Chat Service Connection Failed

**Error**: `httpx.ConnectError: Connection refused`

**Solution**:
```bash
# Check if chat-service is running
curl http://localhost:8000/health

# Check CHAT_SERVICE_URL in .env
# Docker: http://chat-service:8000
# Local: http://localhost:8000
```

#### 4. Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Solution**:
```bash
# Find process using port 8004
lsof -i :8004  # Linux/Mac
netstat -ano | findstr :8004  # Windows

# Kill process or change port in .env
PORT=8005
```

#### 5. Memory Issues

**Error**: Service crashes with `MemoryError`

**Solution**:
```python
# Clear conversation memories periodically
service.clear_conversation_memory(conversation_id)

# Or use summary memory for long conversations
workflow_type = "summary_memory"
```

### Debug Mode

**Enable Verbose Logging**:
```bash
# .env
LOG_LEVEL=DEBUG
LANGCHAIN_VERBOSE=true
```

**Check Logs**:
```bash
# Docker
docker logs -f langchain-service

# Local
# Logs appear in console
```

### Performance Issues

**Slow Responses**:
1. Check OpenAI API status
2. Monitor network latency to chat-service
3. Review conversation memory size
4. Consider using summary memory

**High Memory Usage**:
1. Clear conversation memories
2. Restart service periodically
3. Implement memory TTL (future enhancement)

---

## 🤝 Contributing Guidelines

### Code Style

**Follow PEP 8**:
```bash
# Install formatter
pip install black isort

# Format code
black app/
isort app/
```

**Type Hints**:
```python
# ✅ Good
async def process_message(
    conversation_id: str,
    message: str
) -> Dict[str, Any]:
    pass

# ❌ Bad
async def process_message(conversation_id, message):
    pass
```

### Adding New Workflows

1. **Create workflow method**:
```python
async def process_new_workflow(
    self,
    conversation_id: str,
    user_message: str
) -> Dict[str, Any]:
    # Implementation
    pass
```

2. **Add API endpoint**:
```python
@router.post("/conversations/{id}/message/new-workflow")
async def send_message_new_workflow(...):
    pass
```

3. **Update documentation**:
- Add to README.md
- Update API docs
- Add examples

4. **Add tests**:
```python
def test_new_workflow():
    # Unit tests
    pass
```

### Commit Messages

**Format**:
```
type(scope): description

[optional body]

[optional footer]
```

**Examples**:
```
feat(workflow): add RAG workflow
fix(client): handle connection timeout
docs(readme): update installation guide
test(api): add integration tests
```

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Update documentation
6. Submit PR with description

---

## 📚 Additional Resources

### LangChain Documentation
- [LangChain Docs](https://python.langchain.com/)
- [LangChain OpenAI Integration](https://python.langchain.com/docs/integrations/platforms/openai)
- [Memory Types](https://python.langchain.com/docs/modules/memory/)

### FastAPI Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Async Programming](https://fastapi.tiangolo.com/async/)
- [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)

### OpenAI Documentation
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Chat Completions](https://platform.openai.com/docs/guides/chat)
- [Best Practices](https://platform.openai.com/docs/guides/production-best-practices)

### Docker Documentation
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 📝 Version History

### v1.0.0 (2025-11-19)
- Initial release
- Simple chain workflow
- Structured chain workflow
- Summary memory workflow
- Chat-service integration
- Docker support
- Complete documentation

---

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review API docs at `/docs`
3. Check logs for errors
4. Verify configuration
5. Test dependencies are running

**Happy Developing! 🚀**
