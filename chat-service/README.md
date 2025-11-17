# OpenAI ChatBot Service

A comprehensive FastAPI application that provides OAuth 2.0 authenticated AI-powered conversations with real-time WebSocket support and OpenAI integration.

## 🌟 Overview

The ChatBot Service is the main application component of the ConvoAI platform, providing:
- **AI-Powered Conversations**: Integration with OpenAI's GPT models
- **Real-time Communication**: WebSocket support for instant messaging
- **OAuth 2.0 Security**: Token-based authentication with role-based access control
- **Conversation Management**: Persistent storage of chat history
- **User-Scoped Access**: Users can only access their own conversations
- **Hash-Based IDs**: Secure, obfuscated identifiers for users and conversations
- **Analytics Integration**: Middleware for tracking conversation metrics

## 🔐 OAuth 2.0 Integration

This service integrates with the Authorization Server for secure authentication:

### Authentication Flow
1. User logs in via Authorization Server and receives JWT token
2. Client includes token in `Authorization: Bearer <token>` header
3. Service validates token using shared `AUTH_SECRET_KEY`
4. Request is authorized based on user roles and ownership
5. Response is returned to authenticated user

### Security Levels
- **Public Endpoints**: No authentication required (health check)
- **Authenticated Endpoints**: Valid JWT token required
- **User-Scoped Endpoints**: Users can only access their own resources
- **Admin Endpoints**: Admin role required

## ✨ Features

### 🔒 Security & Authentication
- **OAuth 2.0 Integration** - JWT token validation
- **Role-Based Access Control** - Admin, User, Manager roles
- **User-Scoped Resources** - Strict ownership validation
- **WebSocket Authentication** - Token validation for real-time connections
- **Hash-Based IDs** - Obfuscated user/conversation identifiers (16/12/10 char)

### 🔧 User & Conversation Management
- **User CRUD Operations** - Create, read, update, delete users (Admin only)
- **Conversation Management** - Start, end, reconnect to conversations
- **Message History** - Complete conversation persistence
- **Advanced Filtering** - Search, pagination, and filtering options

### 💬 Real-time Chat
- **WebSocket Support** - Real-time bidirectional communication
- **OpenAI Integration** - AI-powered conversations using GPT models
- **Context Preservation** - Maintain conversation history in database
- **Multi-user Support** - Handle multiple concurrent conversations
- **Anonymous Chat** - Optional anonymous WebSocket connections

### 📊 Analytics Integration
- **Middleware Tracking** - Automatic metrics collection
- **Conversation Events** - Track creation, messaging, and engagement
- **User Activity** - Monitor user interactions
- **Response Times** - Track API performance

### 🏗️ Architecture
- **Microservices Design** - Separate auth, chat, and analytics services
- **Docker Ready** - Full containerization support
- **Database Persistence** - SQLite with absolute paths
- **Modular Design** - Clean separation of concerns
- **Async Support** - Full asynchronous operations

## 🚀 Quick Start

### Docker Deployment (Recommended)

Run with full platform from project root:

```bash
docker-compose up chat-service
```

See main [README.md](../README.md) for complete Docker setup.

### Local Development

**Prerequisites:**
- Python 3.12+
- OpenAI API Key
- Auth service running (for authentication)

**Setup:**

1. **Install dependencies:**
   ```bash
   cd chat-service
   pip install -e .
   
   # For development
   pip install -e .[dev]
   ```

2. **Configure environment:**
   
   Ensure root `.env` exists:
   ```env
   # ConvoAI/.env
   AUTH_SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-key-here
   ```
   
   Service `.env`:
   ```env
   # chat-service/.env
   PORT=8000
   HOST=0.0.0.0
   AUTH_SERVICE_URL=http://localhost:8001
   ANALYTICS_SERVICE_URL=http://localhost:8002
   CORS_ORIGINS=http://localhost:3000
   ```

3. **Run the service:**
   ```bash
   # Method 1: Using uvicorn
   uvicorn main:app --reload --port 8000
   
   # Method 2: Using Python directly
   python main.py
   ```

**Using Platform Scripts** (from project root):

**Windows:**
```cmd
scripts\windows\start-chat-service.bat
```

**Linux/Mac:**
```bash
scripts/linux-mac/start-chat-service.sh
```

### Access Points

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws/{conversation_id}

### Database Configuration

Database is automatically created at `chat-service/data/chatbot.db` using absolute paths. No manual configuration needed.

To reset database:

**Windows:**
```cmd
del chat-service\data\chatbot.db
```

**Linux/Mac:**
```bash
rm chat-service/data/chatbot.db
```

Then restart the service to recreate.
# Build and start services
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f openai-chatbot

# Restart a specific service
docker-compose restart openai-chatbot

# Production deployment with nginx
docker-compose --profile production up -d --build
```

### Option 2: Individual Docker Container

Build and run the FastAPI application as a standalone Docker container.

#### 1. Build the Docker Image

```bash
# Navigate to the application directory
cd chat-service

# Build development image
docker build -t openai-web-service:dev .

# Or build production image (optimized)
docker build -f Dockerfile.production -t openai-web-service:prod .
```

#### 2. Run the Container

```bash
# Basic run (development)
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-openai-api-key-here \
  openai-web-service:dev

# Production run with volume mounts
docker run -d \
  --name openai-chatbot \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-openai-api-key-here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  openai-web-service:prod

# Run with custom port
docker run -p 3000:8000 \
  -e OPENAI_API_KEY=your-openai-api-key-here \
  -e PORT=8000 \
  openai-web-service:dev
```

#### 3. Container Management

```bash
# View running containers
docker ps

# View container logs
docker logs openai-chatbot

# Follow logs in real-time
docker logs -f openai-chatbot

# Stop container
docker stop openai-chatbot

# Remove container
docker rm openai-chatbot

# Access container shell (debugging)
docker exec -it openai-chatbot /bin/bash
```

### Production Deployment

For production environments, use the optimized setup:

```bash
# 1. Build production image
docker build -f chat-service/Dockerfile.production -t openai-web-service:latest .

# 2. Run with production configuration
docker-compose --profile production up -d --build
```

This includes:
- ✅ **Nginx reverse proxy** with rate limiting
- ✅ **Multi-stage Docker build** for smaller images
- ✅ **Health checks** for container monitoring
- ✅ **Volume mounts** for data persistence
- ✅ **Security headers** and SSL support
- ✅ **Automatic restarts** on failure

### Docker Services Overview

When using `docker-compose up --profile production`:

| Service | Port | Description |
|---------|------|-------------|
| **openai-chatbot** | 8000 | Main FastAPI application |
| **nginx** | 80, 443 | Reverse proxy with load balancing |

### Accessing Services

| Service | URL | Description |
|---------|-----|-------------|
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/health | Service health status |
| **WebSocket Chat** | ws://localhost:8000/ws/chat | Real-time chat endpoint |
| **Production (via Nginx)** | http://localhost | Load-balanced access |

### Troubleshooting Docker

#### Common Issues and Solutions

**1. Import Error: "attempted relative import with no known parent package"**

This error occurs when the application can't resolve relative imports. The fix is already implemented in `app.py` with fallback imports.

If you encounter this issue:
```bash
# Rebuild the container to ensure latest fixes
docker-compose build --no-cache openai-chatbot
docker-compose up
```

**2. OpenAI API Key Issues**
```bash
# Check if the API key is set correctly
docker-compose exec openai-chatbot env | grep OPENAI

# Set the key in your environment before running
export OPENAI_API_KEY=your-actual-api-key
docker-compose up
```

**3. Port Already in Use**
```bash
# Check what's using port 8000
netstat -tulpn | grep :8000

# Use a different port
docker-compose up -p 8001:8000
```

**4. Container Won't Start**
```bash
# Check container logs for detailed error messages
docker-compose logs openai-chatbot

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart openai-chatbot
```

#### General Debugging Commands

```bash
# Check container status
docker-compose ps

# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f openai-chatbot

# View logs from specific time
docker-compose logs --since="1h" openai-chatbot

# Rebuild specific service
docker-compose build openai-chatbot

# Clean rebuild (removes cache)
docker-compose build --no-cache openai-chatbot

# Execute commands inside container
docker-compose exec openai-chatbot /bin/bash

# Check resource usage
docker stats

# Clean up unused resources
docker system prune -a

# Remove all containers and volumes
docker-compose down -v --remove-orphans
```

#### Performance Optimization

```bash
# For production, limit container resources
docker run --memory="512m" --cpus="1.0" openai-web-service

# Monitor container performance
docker stats openai-chatbot-api

# Scale services (if using swarm mode)
docker service scale chatbot=3
```

## 🔐 OAuth 2.0 Authenticated Endpoints

All API endpoints require OAuth 2.0 authentication unless otherwise noted. Include the JWT token in the `Authorization` header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### User Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/users/` | POST | Admin | Create new user |
| `/api/v1/users/` | GET | Admin | List all users |
| `/api/v1/users/{user_id}` | GET | Authenticated | Get user details (own or admin) |

### Conversation Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/users/{user_id}/conversations/` | POST | User-scoped | Create conversation (own or admin) |
| `/api/v1/users/{user_id}/conversations/` | GET | User-scoped | List conversations (own or admin) |
| `/api/v1/users/{user_id}/conversations/{conversation_id}/reconnect` | POST | User-scoped | Reconnect to conversation |
| `/api/v1/users/{user_id}/conversations/{conversation_id}/validate` | GET | User-scoped | Validate conversation access |
| `/api/v1/users/{user_id}/conversations/recent` | GET | User-scoped | Get recent conversations |
| `/api/v1/users/{user_id}/conversations/{conversation_id}/end` | POST | User-scoped | End conversation |
| `/api/v1/users/{user_id}/conversations/{conversation_id}/stats` | GET | User-scoped | Get conversation statistics |
| `/api/v1/users/{user_id}/conversations/{conversation_id}` | DELETE | User-scoped | Delete conversation (owner or admin) |

### Message Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/conversations/{conversation_id}/messages/` | POST | Owner | Add message to conversation |
| `/api/v1/conversations/{conversation_id}/messages/` | GET | Owner | Get conversation messages |

### Authorization Levels

**Admin Only**: Only users with `admin` role can access
```python
# Example: Create user endpoint
@router.post("/users/", dependencies=[Depends(require_admin)])
```

**User-Scoped**: Users can only access their own resources, admins can access all
```python
# Example: Users can only view their own conversations
if not current_user.is_admin() and current_user.user_id != user_id:
    raise HTTPException(status_code=403, detail="Access denied")
```

**Owner Only**: Only the conversation owner can access
```python
# Example: Only conversation owner can add messages
if not current_user.is_admin() and current_user.user_id != conversation.user_id:
    raise HTTPException(status_code=403, detail="Access denied")
```

## WebSocket Chat Endpoints

### Authenticated WebSocket (Recommended)
```
ws://localhost:8000/ws/chat/{user_id}?token=YOUR_JWT_TOKEN
```

**Features**:
- Requires valid JWT token
- Token validation before connection
- User ID must match token payload
- Full access to user-scoped conversations

**Example**:
```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
const userId = "ABC123DEF4567890";

const ws = new WebSocket(`ws://localhost:8000/ws/chat/${userId}?token=${token}`);

ws.onopen = () => {
  console.log("Authenticated connection established");
};

ws.onerror = (error) => {
  // Token validation failed or user_id mismatch
  console.error("WebSocket error:", error);
};
```

### Anonymous WebSocket
```
ws://localhost:8000/ws/chat
```

**Features**:
- No authentication required
- Limited access
- Conversations not saved to user profile
- Useful for demos and testing

**Example**:
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/chat");

ws.onopen = () => {
  console.log("Anonymous connection established");
};
```

## WebSocket Message Format

### 1. Start Conversation
```json
{
  "type": "start_conversation",
  "data": {
    "user_id": 123,
    "title": "My Conversation",
    "system_message": "You are a helpful assistant"
  }
}
```

### 2. Send Message
```json
{
  "type": "send_message",
  "data": {
    "conversation_id": 456,
    "content": "Hello, how are you?"
  }
}
```

### 3. End Conversation
```json
{
  "type": "end_conversation",
  "data": {
    "conversation_id": 456
  }
}
```

## Project Structure

```
Open-ChatBot/
├── docker-compose.yml           # 🐳 Docker Compose configuration
├── .venv/                      # Python virtual environment (local dev)
└── chat-service/         # Main application directory
    ├── 📱 Application Files
    ├── app.py                  # Main FastAPI application
    ├── main.py                 # Entry point
    ├── 🐳 Docker Files
    ├── Dockerfile              # Development Docker image
    ├── Dockerfile.production   # Production-optimized Docker image  
    ├── .dockerignore          # Docker build exclusions
    ├── nginx.conf             # Nginx reverse proxy configuration
    ├── 📊 Configuration
    ├── .env.example           # Environment variables template
    ├── pyproject.toml         # Project dependencies and metadata
    ├── requirements.txt       # Python dependencies
    ├── 🏗️ Application Architecture
    ├── engine/                # Database layer
    │   ├── database.py        # Database configuration
    │   ├── models.py          # SQLAlchemy models
    │   ├── schemas.py         # Pydantic schemas
    │   ├── crud.py           # Main CRUD (imports from specialized modules)
    │   ├── user_crud.py      # User-specific CRUD operations
    │   ├── item_crud.py      # Item-specific CRUD operations
    │   └── conversation_crud.py # Conversation & message CRUD operations
    ├── api/                   # HTTP endpoints
    │   └── crud_routes.py     # CRUD API routes
    ├── services/              # Business logic
    │   └── openai_service.py  # OpenAI integration with logging
    ├── websocket/             # WebSocket handlers
    │   └── chat_handler.py    # WebSocket chat logic
    ├── utilities/             # Reusable utility functions
    │   ├── database_utils.py  # Generic database operations
    │   ├── validation_utils.py # Data validation and sanitization
    │   ├── response_utils.py  # API response formatting
    │   ├── datetime_utils.py  # Date and time operations
    │   └── logging_utils.py   # Structured logging utilities
    ├── 📚 Documentation & Testing
    ├── README.md              # Project documentation
    ├── REFACTORING_SUMMARY.md # Code refactoring documentation
    └── test_api.py            # API integration tests
```

## Utilities Overview

### 🗄️ Database Utils (`utilities/database_utils.py`)
- **Generic CRUD Operations**: Reusable functions for create, read, update, delete
- **Pagination & Filtering**: Generic pagination with filtering support
- **Search Functionality**: Multi-field text search across entities
- **Batch Operations**: Bulk create and update operations
- **Existence Checks**: Utility functions to check if entities exist

### ✅ Validation Utils (`utilities/validation_utils.py`)
- **Email Validation**: Email format validation using email-validator
- **String Sanitization**: Text cleaning and length validation
- **Username Validation**: Username format and length checks
- **Price Validation**: Numeric validation for pricing fields
- **Search Query Validation**: Safe search query sanitization
- **File Validation**: Filename and extension validation

### 📤 Response Utils (`utilities/response_utils.py`)
- **Standardized Responses**: Consistent API response formatting
- **Error Handling**: Structured error response creation
- **Pagination Responses**: Formatted paginated data responses
- **Model Serialization**: SQLAlchemy model to dict conversion
- **WebSocket Responses**: WebSocket message formatting
- **Health Check Responses**: System health status formatting

### 📅 DateTime Utils (`utilities/datetime_utils.py`)
- **UTC Operations**: Standardized UTC datetime handling
- **Format Conversion**: DateTime to string and vice versa
- **Timezone Handling**: Timezone conversion and management
- **Human-Readable Times**: "Time ago" formatting
- **Duration Calculations**: Time difference calculations
- **Date Range Operations**: Date range validation and creation

### 📝 Logging Utils (`utilities/logging_utils.py`)
- **Structured Logging**: JSON-formatted log entries
- **API Request/Response Logging**: HTTP request and response tracking
- **Database Operation Logging**: Database action auditing
- **WebSocket Event Logging**: Real-time communication tracking
- **OpenAI API Logging**: AI service interaction monitoring
- **Security Event Logging**: Security-related event tracking
- **Performance Logging**: Response time and performance metrics

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required for chat)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload in development (default: false in Docker)
- `WORKERS`: Number of worker processes for production (default: 1)

### Docker Configuration Files

| File | Purpose | Description |
|------|---------|-------------|
| `Dockerfile` | Development container | Standard Docker image for development |
| `Dockerfile.production` | Production container | Multi-stage optimized build for production |
| `docker-compose.yml` | Service orchestration | Defines all services and their configuration |
| `.dockerignore` | Build optimization | Excludes unnecessary files from Docker build |
| `nginx.conf` | Reverse proxy config | Nginx configuration for production deployment |

### Docker Environment Variables

When running with Docker, you can set these additional variables:

```bash
# Docker Compose environment variables
COMPOSE_PROJECT_NAME=openai-chatbot    # Project name for containers
OPENAI_API_KEY=your-key-here          # Required: OpenAI API key
PORT=8000                             # Application port
HOST=0.0.0.0                         # Bind address
RELOAD=false                          # Auto-reload (set to true for development)
WORKERS=1                             # Number of worker processes

# Volume mount paths
DATA_PATH=./data                      # Database storage path
LOGS_PATH=./logs                      # Application logs path
```

### Production Configuration

For production deployment, additional considerations:

```bash
# Security
- Use HTTPS with proper SSL certificates
- Set strong API keys and secrets
- Configure firewall rules
- Enable container resource limits

# Performance  
- Set appropriate worker count based on CPU cores
- Configure nginx worker processes
- Set up log rotation
- Monitor resource usage

# Reliability
- Configure health checks
- Set up backup strategies for data volumes
- Implement monitoring and alerting
- Use container restart policies
```

## License

MIT License

