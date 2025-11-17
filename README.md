# ConvoAI - Intelligent Conversation Platform

A production-ready, full-stack AI conversation platform featuring a React frontend, OAuth 2.0 authentication, real-time WebSocket communication, and OpenAI integration. Built with React and FastAPI for a complete microservices solution.

## 🌟 Overview

This platform consists of four main components working together to provide a secure, intelligent chatbot experience with comprehensive analytics:

1. **React Chat Frontend** (Port 3000) - Modern, responsive web UI with real-time messaging and integrated analytics panel
2. **Authorization Server** (Port 8001) - OAuth 2.0 authentication and role-based access control
3. **ChatBot Service** (Port 8000) - AI-powered conversations with OpenAI and WebSocket support
4. **Analytics Service** (Port 8002) - Admin-only analytics and metrics tracking with real-time updates

### 🚀 Deployment Options

- **Docker**: Containerized deployment with Docker Compose (recommended for production)
- **Local Development**: Run services directly on Windows, macOS, or Linux using platform-specific scripts

### 🎯 Key Highlights

- 📊 **Integrated Analytics Panel**: View metrics alongside chat without leaving the conversation
- 🔄 **Real-time Tracking**: Automatic refresh of analytics data every 30 seconds
- 🎫 **Token Tracking**: Monitor OpenAI API token usage across all conversations
- 👥 **User Activity**: Track active users, conversations, and message counts
- 🚀 **Production Ready**: Comprehensive tracking middleware and public API endpoints

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│                    http://localhost:3000                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│                    http://localhost:3000                         │
│  Features: Chat Interface + Real-time Analytics Side Panel       │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                    React Chat Frontend                          │
│                      (Port 3000)                                │
│  - Login/Register UI         - Analytics Side Panel            │
│  - Chat Interface            - State Management                 │
│  - WebSocket Client          - OAuth 2.0 Integration            │
│  - Conversation List         - Real-time Metrics Display        │
└──────┬─────────────────────────────────────────┬──────┬─────────┘
       │                                         │      │
       │ Auth                                    │      │ Analytics
       │                                         │      │ (Admin)
       ▼                                         ▼      ▼
┌──────────────────┐    ┌──────────────────┐   ┌──────────────────┐
│ Auth Server      │    │ ChatBot Service  │   │ Analytics Service│
│  (Port 8001)     │◄───│   (Port 8000)    │──►│   (Port 8002)    │
│                  │    │                  │   │                  │
│ - User Mgmt      │    │ - Conversation   │   │ - Metrics Track  │
│ - JWT Tokens     │    │ - Messages       │   │ - Activity Logs  │
│ - RBAC           │    │ - WebSocket      │   │ - User Stats     │
│ - Activity Track │───►│ - OpenAI API     │   │ - Token Counting │
│                  │    │ - Analytics MW   │───│ - Admin API      │
└────────┬─────────┘    └────────┬─────────┘   └────────┬─────────┘
         │                       │                      │
         ▼                       ▼                      ▼
  ┌─────────────┐        ┌──────────────┐      ┌──────────────┐
  │  auth.db    │        │conversations.│      │ analytics.db │
  │  (SQLite)   │        │   db         │      │  (SQLite)    │
  │             │        │  (SQLite)    │      │              │
  │ - users     │        │              │      │ - user_activity
  │ - roles     │        │- conversations      │ - conversations
  │ - user_roles│        │- messages    │      │ - messages   │
  └─────────────┘        └──────────────┘      │ - api_usage  │
                                               │ - daily_stats│
                                               └──────────────┘
```

## ✨ Key Features

### Frontend (React)
- 🎨 **Modern UI**: Gradient themes, responsive design, smooth animations
- 🔐 **Secure Authentication**: OAuth 2.0 with JWT tokens
- 💬 **Real-time Chat**: WebSocket-based instant messaging
- 📊 **Analytics Side Panel**: View metrics alongside conversations (Admin-only)
  - Total users, active users, conversations, messages, tokens
  - Recent user activity with timestamps
  - Most active users leaderboard
  - Auto-refresh every 30 seconds
  - Manual refresh button
- 📱 **Mobile Responsive**: Works on all device sizes
- 🔄 **Auto-reconnect**: Automatic WebSocket reconnection
- 📝 **Conversation Management**: Create, view, delete conversations

### Backend Services
- 🔒 **OAuth 2.0 Security**: Industry-standard authentication
- 👥 **User Management**: Registration, login, profile management
- 🎭 **Role-Based Access Control**: Admin, user, manager roles
- 🤖 **OpenAI Integration**: AI-powered chat responses
- 🔌 **WebSocket Support**: Real-time bidirectional communication
- 🔑 **Hash-based IDs**: Secure, non-sequential identifiers
- 📊 **RESTful API**: Complete CRUD operations
- 📈 **Analytics Tracking**: Comprehensive metrics and activity logging
  - Automatic API usage tracking via middleware
  - User activity tracking (login, logout, conversations)
  - Message and token counting
  - Conversation metrics (message count, tokens, response time)
  - Public tracking endpoints for service-to-service communication
  - Admin-protected analytics dashboard API
- 🏥 **Health Checks**: Service monitoring endpoints

## 📦 Project Structure

```
ConvoAI/
├── .env                          # Shared configuration (AUTH_SECRET_KEY, OPENAI_API_KEY)
├── .env.example                  # Example environment configuration
├── docker-compose.yml            # Docker orchestration
├── README.md                     # This file
├── QUICK_START_LOCAL.md          # Detailed local setup guide
│
├── scripts/                      # Platform-specific service management scripts
│   ├── windows/                  # Windows scripts (.bat)
│   │   ├── setup-venv.bat        # Create virtual environments
│   │   ├── start-all-services.bat # Start all services
│   │   ├── start-auth-service.bat
│   │   ├── start-chat-service.bat
│   │   ├── start-analytics-service.bat
│   │   ├── start-frontend.bat
│   │   ├── stop-all-services.bat # Stop all services
│   │   ├── setup-admin.bat       # Create admin user
│   │   ├── setup-admin.py        # Admin user management
│   │   ├── list-admins.bat       # List admin users
│   │   ├── run-tests.bat         # Run test suite
│   │   └── check-services.bat    # Health check
│   ├── linux-mac/                # Linux/Mac scripts (.sh)
│   │   ├── setup-venv.sh
│   │   ├── start-all-services.sh
│   │   ├── start-auth-service.sh
│   │   ├── start-chat-service.sh
│   │   ├── start-analytics-service.sh
│   │   ├── start-frontend.sh
│   │   ├── stop-all-services.sh
│   │   ├── setup-admin.sh
│   │   ├── setup-admin.py
│   │   ├── list-admins.sh
│   │   ├── run-tests.sh
│   │   └── check-services.sh
│   └── README.md                 # Scripts documentation
│
├── chat-frontend/                # React frontend application
│   ├── src/
│   │   ├── components/           # UI components
│   │   │   ├── ChatWindow.js
│   │   │   ├── ConversationList.js
│   │   │   ├── MessageList.js
│   │   │   ├── MessageInput.js
│   │   │   └── MetricsCard.js    # Analytics metric cards
│   │   ├── contexts/
│   │   │   └── AuthContext.js    # Auth state management
│   │   ├── hooks/
│   │   │   ├── useChat.js
│   │   │   └── useConversations.js
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── ChatPage.js       # Main chat with analytics panel
│   │   │   └── AnalyticsDashboard.js  # Full analytics page
│   │   ├── services/
│   │   │   ├── authService.js    # Auth API client
│   │   │   ├── chatService.js    # Chat API client
│   │   │   ├── analyticsService.js # Analytics API client
│   │   │   └── websocketService.js
│   │   ├── App.js                # Main app with routing
│   │   └── index.js
│   ├── .env                      # Frontend environment variables
│   ├── .env.example              # Example frontend configuration
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── README.md
│
├── auth-service/                 # OAuth 2.0 authentication server
│   ├── auth_server/
│   │   ├── main.py               # FastAPI app
│   │   ├── database/             # DB configuration
│   │   ├── models/               # SQLAlchemy models
│   │   ├── routers/              # API routes
│   │   ├── schemas/              # Pydantic schemas
│   │   └── security/             # Auth logic
│   ├── tests/
│   └── Dockerfile
│
├── openai_web_service/            # ChatBot service
│   ├── api/
│   │   └── routes.py             # API endpoints
│   ├── engine/
│   │   ├── conversation_crud.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── security/
│   │   └── oauth.py              # OAuth integration
│   ├── websocket/
│   │   └── chat_handler.py       # WebSocket handler
│   ├── middleware/
│   │   └── analytics_middleware.py # Analytics tracking
│   ├── services/
│   │   └── openai_service.py
│   ├── utilities/
│   │   └── hash_utils.py         # ID generation
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── analytics-service/             # Analytics service
│   ├── analytics/
│   │   ├── database/             # DB configuration
│   │   ├── models/               # Analytics models
│   │   │   └── analytics.py      # Metrics models
│   │   ├── routers/              # API routes
│   │   │   └── analytics.py      # Analytics endpoints
│   │   ├── schemas/              # Pydantic schemas
│   │   │   └── analytics.py      # Response schemas
│   │   ├── services/             # Business logic
│   │   │   └── analytics_service.py
│   │   └── security/             # Auth logic
│   │       └── auth.py           # JWT validation
│   ├── .env                      # Service environment variables
│   ├── .env.example              # Example service configuration
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── tests/                         # End-to-end test suite
│   ├── test_0_smoke.py           # Quick smoke tests
│   ├── test_1_auth_service.py    # Authentication tests
│   ├── test_2_chat_api.py        # Chat API tests
│   ├── test_3_websocket.py       # WebSocket tests
│   ├── test_4_end_to_end.py      # Full integration tests
│   ├── conftest.py               # Test configuration
│   ├── requirements.txt          # Test dependencies
│   ├── run_tests.bat             # Windows test runner
│   ├── run_tests.sh              # Linux/Mac test runner
│   └── README.md
│
├── docker-compose.yml             # Docker orchestration
├── .env                           # Shared configuration (AUTH_SECRET_KEY, OPENAI_API_KEY)
├── .env.example                   # Example environment configuration
├── CHANGELOG.md                   # Version history
└── README.md                      # This file
```

## 🧪 Testing

Comprehensive end-to-end test suite covering all functionality:

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_1_auth_service.py -v    # Authentication tests
pytest tests/test_2_chat_api.py -v        # Chat API tests
pytest tests/test_3_websocket.py -v       # WebSocket tests
pytest tests/test_4_end_to_end.py -v      # End-to-end integration tests

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Quick smoke test
pytest tests/test_0_smoke.py -v
```

**Using Test Runner Scripts:**

```bash
# Linux/Mac
chmod +x tests/run_tests.sh
./tests/run_tests.sh              # All tests
./tests/run_tests.sh coverage     # With coverage report

# Windows
tests\run_tests.bat               # All tests
tests\run_tests.bat coverage      # With coverage report
```

**Test Coverage:**
- ✅ 50+ test cases across 4 test files
- ✅ User registration and authentication flow
- ✅ Conversation and message management
- ✅ WebSocket real-time communication
- ✅ Role-based access control
- ✅ Multi-user scenarios
- ✅ Error handling and recovery
- ✅ Complete user journey testing

See [tests/README.md](tests/README.md) for detailed testing documentation.

## 🚀 Quick Start

Choose your deployment method:

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker & Docker Compose
- OpenAI API Key

**Steps:**

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd AI-Chat-Bot
   ```

2. **Configure Environment**
   
   Edit `.env` file in project root:
   ```env
   # Shared Secret Key (IMPORTANT: Change in production!)
   AUTH_SECRET_KEY=f7e8d9c6b5a4930281f6e5d4c3b2a19087f6e5d4c3b2a19087f6e5d4c3b2a190
   
   # OpenAI API Key
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

3. **Start All Services**
   ```bash
   docker-compose up --build
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - Login: `admin` / `admin123`

### Option 2: Local Development

**Prerequisites:**
- Python 3.12+
- Node.js 18+
- OpenAI API Key

**Windows:**

```cmd
REM 1. Setup virtual environments (first time only)
scripts\windows\setup-venv.bat

REM 2. Create admin user (first time only)
scripts\windows\setup-admin.bat

REM 3. Start all services
scripts\windows\start-all-services.bat

REM 4. Access: http://localhost:3000
```

**Linux/Mac:**

```bash
# 1. Make scripts executable (first time only)
chmod +x scripts/linux-mac/*.sh

# 2. Setup virtual environments (first time only)
./scripts/linux-mac/setup-venv.sh

# 3. Create admin user (first time only)
./scripts/linux-mac/setup-admin.sh

# 4. Start all services
./scripts/linux-mac/start-all-services.sh

# 5. Access: http://localhost:3000
```

**📚 For detailed local setup instructions, see [QUICK_START_LOCAL.md](QUICK_START_LOCAL.md)**

## 📖 Usage Guide

### User Registration

1. Navigate to `http://localhost:3000/register`
2. Fill in:
   - Username
   - Email
   - Password (min 6 characters)
   - Full Name (optional)
3. Click "Create Account"
4. Redirected to login page

### Login

1. Navigate to `http://localhost:3000/login`
2. Enter username and password
3. Click "Sign In"
4. Redirected to chat interface

### Creating Conversations

1. Click ➕ button in sidebar
2. Enter conversation title
3. Click "Create"
4. Conversation appears in list

### Sending Messages

1. Select conversation from sidebar
2. Type message in input field
3. Press Enter or click 📤
4. Message sent via WebSocket
5. AI response appears in real-time

### Deleting Conversations

1. Hover over conversation in sidebar
2. Click 🗑️ button
3. Confirm deletion

### Using Analytics (Admin Only)

**Integrated Side Panel:**
1. Login as admin user
2. Click "📊 Analytics" button in header
3. Analytics panel appears on right side
4. View metrics while chatting:
   - Total Users
   - Active Users Today
   - Total Conversations
   - Total Messages
   - Total Tokens Used
   - Average Response Time
5. Scroll to see:
   - Recent user activity
   - Most active users
6. Click 🔄 Refresh to update data manually
7. Data auto-refreshes every 30 seconds
8. Click Analytics button again to close panel

**Full Analytics Dashboard:**
1. Navigate to `http://localhost:3000/analytics`
2. View comprehensive metrics and charts
3. Filter user activities
4. Export reports (coming soon)

## 🔧 Development

### Local Development Setup

Detailed guide available in [QUICK_START_LOCAL.md](QUICK_START_LOCAL.md)

**Prerequisites:**
- Python 3.12+
- Node.js 18+
- OpenAI API Key

**Quick Steps:**

1. **Clone and Configure:**
   ```bash
   git clone <repository-url>
   cd AI-Chat-Bot
   ```

2. **Create Root .env:**
   ```
   AUTH_SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-key-here
   ```

3. **Setup Virtual Environments:**
   
   **Windows:**
   ```cmd
   scripts\windows\setup-venv.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x scripts/linux-mac/setup-venv.sh
   scripts/linux-mac/setup-venv.sh
   ```

4. **Create Admin User:**
   
   **Windows:**
   ```cmd
   scripts\windows\setup-admin.bat
   ```
   
   **Linux/Mac:**
   ```bash
   scripts/linux-mac/setup-admin.sh
   ```

5. **Start All Services:**
   
   **Windows:**
   ```cmd
   scripts\windows\start-all-services.bat
   ```
   
   **Linux/Mac:**
   ```bash
   scripts/linux-mac/start-all-services.sh
   ```

**Service URLs:**
- Frontend: http://localhost:3000
- Auth Service: http://localhost:8001
- Chat Service: http://localhost:8000
- Analytics Service: http://localhost:8002

### Docker Development

Use Docker Compose for containerized development.

**Frontend Development:**

```bash
cd chat-frontend
npm install
npm start
```

Runs on `http://localhost:3000` with hot reload.

**Backend Development:**

**Auth Server:**
```bash
cd auth-service
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn auth_server.main:app --reload --port 8001
```

**Chat Service:**
```bash
cd openai_web_service
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Analytics Service:**
```bash
cd analytics-service
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8002
```

### Environment Configuration

The project uses a 3-tier environment configuration:

1. **Root .env** (shared secrets):
   - `AUTH_SECRET_KEY` - JWT signing key (shared across all services)
   - `OPENAI_API_KEY` - OpenAI API access

2. **Service .env files** (service-specific):
   - Port configuration (PORT)
   - Host configuration (HOST)
   - CORS origins
   - Service URLs (AUTH_SERVICE_URL, CHAT_SERVICE_URL)

3. **Automatic database paths**:
   - No DATABASE_URL needed in .env files
   - Services automatically create databases with absolute paths
   - auth-service: `auth-service/auth.db`
   - openai_web_service: `openai_web_service/data/chatbot.db`
   - analytics-service: `analytics-service/data/analytics.db`

### Admin User Management

**Create Admin User:**

**Windows:**
```cmd
scripts\windows\setup-admin.bat
```

**Linux/Mac:**
```bash
scripts/linux-mac/setup-admin.sh
```

Defaults:
- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com`

**List Admin Users:**

**Windows:**
```cmd
scripts\windows\list-admins.bat
```

**Linux/Mac:**
```bash
scripts/linux-mac/list-admins.sh
```

**Change admin password after first login!**

## 📡 API Documentation

### Authentication Service (Port 8001)

**Interactive Docs:** `http://localhost:8001/docs`

**Register User**
```bash
POST /users/
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123",
  "full_name": "John Doe"
}
```

**Login (Get Token)**
```bash
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=john&password=secret123

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "token_type": "bearer"
}
```

**Get Current User**
```bash
GET /auth/me
Authorization: Bearer <token>
```

### ChatBot Service (Port 8000)

**Interactive Docs:** `http://localhost:8000/docs`

All endpoints require `Authorization: Bearer <token>` header.

**List Conversations**
```bash
GET /conversations/
Authorization: Bearer <token>
```

**Create Conversation**
```bash
POST /conversations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My New Chat"
}
```

**Get Messages**
```bash
GET /conversations/{conversation_id}/messages
Authorization: Bearer <token>
```

**Send Message**
```bash
POST /conversations/{conversation_id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "conversation_id": "abc123xyz",
  "role": "user",
  "content": "Hello, AI!"
}
```

**Delete Conversation**
```bash
DELETE /api/v1/users/{username}/conversations/{conversation_id}
Authorization: Bearer <token>
```

**WebSocket Connection**
```javascript
ws://localhost:8000/ws/{conversation_id}?token=<jwt_token>
```

### Analytics Service (Port 8002)

**Interactive Docs:** `http://localhost:8002/docs`

**Admin-only endpoints** - All require `Authorization: Bearer <admin-token>` header.

**Get Analytics Summary**
```bash
GET /api/v1/analytics/summary
Authorization: Bearer <admin_token>

Response:
{
  "total_users": 10,
  "active_users_today": 5,
  "total_conversations": 25,
  "total_messages": 150,
  "total_tokens": 45000,
  "total_api_calls": 200,
  "avg_response_time": 0.45,
  "error_rate": 0.02
}
```

**Get User Activities**
```bash
GET /api/v1/analytics/users/activities?limit=10
Authorization: Bearer <admin_token>
```

**Get Top Users**
```bash
GET /api/v1/analytics/users/top?limit=5
Authorization: Bearer <admin_token>
```

**Get Users List with Filter**
```bash
GET /api/v1/analytics/users/list?active_only=true
Authorization: Bearer <admin_token>
```

**Public Tracking Endpoints** (No auth - for service-to-service):
```bash
POST /api/v1/analytics/track/activity-public
POST /api/v1/analytics/track/api-usage-public
POST /api/v1/analytics/track/conversation-public
POST /api/v1/analytics/track/message-public
```

## 🔐 Security Features

### JWT Token-Based Authentication
- Access tokens with configurable expiration
- HS256 algorithm for signing
- Shared secret between services

### Password Security
- BCrypt hashing with salt
- Minimum password requirements enforced

### User Isolation
- Users can only access their own conversations
- Owner-based authorization checks

### Role-Based Access Control
- Admin role for user management
- User role for standard access
- Manager role for extended permissions

### Hash-Based IDs
- Non-sequential identifiers
- User IDs: 16 characters
- Conversation IDs: 12 characters
- Message IDs: 10 characters

## 🐳 Docker Commands

**Build and start all services:**
```bash
docker-compose up --build
```

**Start in detached mode:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop all services:**
```bash
docker-compose down
```

**Remove volumes (clean slate):**
```bash
docker-compose down -v
```

**Rebuild specific service:**
```bash
docker-compose up --build chat-frontend
```

## 🏥 Health Checks

**Auth Server:**
```bash
curl http://localhost:8001/health
```

**ChatBot Service:**
```bash
curl http://localhost:8000/health
```

**Analytics Service:** ⭐ **NEW**
```bash
curl http://localhost:8002/health
```

**React Frontend:**
```bash
curl http://localhost:3000
```

## 🛠️ Troubleshooting

### Local Development Issues

**Services Won't Start:**

1. Check Python version:
   ```bash
   python --version  # Should be 3.12+
   ```

2. Verify virtual environments exist:
   ```bash
   # Windows
   dir auth-service\venv
   dir openai_web_service\venv
   dir analytics-service\venv
   
   # Linux/Mac
   ls -la auth-service/venv
   ls -la openai_web_service/venv
   ls -la analytics-service/venv
   ```

3. Check if ports are already in use:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   netstat -ano | findstr :8001
   netstat -ano | findstr :8002
   netstat -ano | findstr :3000
   
   # Linux/Mac
   lsof -i :8000
   lsof -i :8001
   lsof -i :8002
   lsof -i :3000
   ```

4. Verify root .env exists with correct keys:
   ```
   AUTH_SECRET_KEY=<value>
   OPENAI_API_KEY=<value>
   ```

**Database Issues:**

1. Databases are created automatically with absolute paths
2. No DATABASE_URL needed in .env files
3. To reset databases, delete them directly:
   ```bash
   # Windows
   del auth-service\auth.db
   del openai_web_service\data\chatbot.db
   del analytics-service\data\analytics.db
   
   # Linux/Mac
   rm auth-service/auth.db
   rm openai_web_service/data/chatbot.db
   rm analytics-service/data/analytics.db
   ```
4. Restart services to recreate databases

**Authentication Errors:**

1. Verify AUTH_SECRET_KEY is same in root .env
2. All services must read from root .env (ensured by load_dotenv())
3. Clear browser localStorage: `localStorage.clear()`
4. Check auth-server logs for JWT errors
5. Ensure token hasn't expired (tokens valid for 30 days)

**Script Path Errors:**

Scripts are organized by platform:
- Windows scripts: `scripts\windows\*.bat`
- Linux/Mac scripts: `scripts/linux-mac/*.sh`

Always run from project root directory:
```bash
# Windows
cd c:\path\to\ConvoAI
scripts\windows\start-all-services.bat

# Linux/Mac
cd /path/to/ConvoAI
scripts/linux-mac/start-all-services.sh
```

**Service Health Check:**

**Windows:**
```cmd
scripts\windows\check-services.bat
```

**Linux/Mac:**
```bash
scripts/linux-mac/check-services.sh
```

Or manually:
```bash
curl http://localhost:8001/health  # Auth
curl http://localhost:8000/health  # Chat
curl http://localhost:8002/health  # Analytics
curl http://localhost:3000         # Frontend
```

### Docker Issues

**CORS Issues:**

If you see CORS errors in browser console:

1. Verify backend services have CORS enabled
2. Check allowed origins in service .env files
3. Ensure requests include proper headers
4. Check CORS_ORIGINS in service .env files

### WebSocket Connection Failed

1. Check chat service is running: `docker ps` or check-services script
2. Verify JWT token is valid and not expired
3. Check browser console for error messages
4. Ensure WebSocket URL is correct (ws:// not wss:// for local)
5. Confirm conversation ID exists and belongs to authenticated user

### Conversation Deletion Not Working

The DELETE endpoint is now implemented. If you still encounter issues:

1. Verify JWT token is valid
2. Ensure you own the conversation you're trying to delete
3. Check browser console for specific error messages
4. Verify backend service is running and healthy

### WebSocket Reconnection Issues

The reconnection logic has been fixed. If you still see "Failed to reconnect":

1. Clear browser cache and reload
2. Check if switching conversations works properly
3. Verify WebSocket connections in browser DevTools (Network tab)
4. Ensure auth token hasn't expired

### Analytics Dashboard Issues

If analytics dashboard shows loading spinner indefinitely:

1. Verify analytics service is running on port 8002
2. Check AUTH_SERVICE_URL in analytics-service/.env is set to http://localhost:8001
3. Verify AUTH_SECRET_KEY is same across all services (in root .env)
4. Check browser console for JWT token errors
5. Ensure user is logged in with valid token

**Reset databases:**
```bash
# Docker
docker-compose down -v
docker-compose up --build

# Local
# Delete database files and restart services (see Database Issues above)
```

### Port Conflicts

If ports are already in use:

```bash
# Check what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# Stop docker services
docker-compose down

# Change ports in docker-compose.yml if needed
```

## 📊 Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| React Frontend | 3000 | Web UI |
| Auth Server | 8001 | Authentication API |
| ChatBot Service | 8000 | Chat API & WebSocket |
| Analytics Service | 8002 | Admin-only analytics & metrics ⭐ **NEW** |

## 🔄 Data Flow

### Authentication Flow
```
User → Frontend → POST /auth/token → Auth Server
Auth Server → JWT Token → Frontend → localStorage
Frontend → All API Requests → Authorization: Bearer <token>
```

### Message Flow
```
User Input → Frontend → WebSocket/HTTP → ChatBot Service
ChatBot → Verify Token → Auth Server → Valid/Invalid
If Valid → ChatBot → Save Message → Database
ChatBot → OpenAI API → Get Response
ChatBot → Save Response → Database
ChatBot → WebSocket → Frontend → Display
```

## 📝 Environment Variables

### Frontend (.env)
```env
REACT_APP_AUTH_API_URL=http://localhost:8001
REACT_APP_CHAT_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Backend (.env)
```env
AUTH_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-key-here
```

## 🧪 Testing

### Test Auth Server
```bash
curl -X POST http://localhost:8001/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}'
```

### Test Login
```bash
curl -X POST http://localhost:8001/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test123"
```

### Test Authenticated Endpoint
```bash
curl http://localhost:8000/conversations/ \
  -H "Authorization: Bearer <your-token>"
```

## 📚 Additional Documentation

- [Quick Start Local Development](./QUICK_START_LOCAL.md) ⭐ **NEW** - Detailed local setup guide
- [Scripts Documentation](./scripts/README.md) - Platform-specific management scripts
- [Frontend README](./chat-frontend/README.md)
- [Auth Server README](./auth-service/README.md)
- [ChatBot Service README](./openai_web_service/README.md)
- [Analytics Service README](./analytics-service/README.md)
- [**Analytics Integration Guide**](./ANALYTICS_GUIDE.md) ⭐ - Complete analytics documentation
- [CHANGELOG](./CHANGELOG.md) - Complete change history
- [Testing Documentation](./tests/README.md)

## 🐛 Known Issues & Fixes

All major issues have been resolved in the latest version:

- ✅ **Login failures** - Fixed JWT token SECRET_KEY configuration
- ✅ **Conversation creation** - Fixed user auto-provisioning
- ✅ **WebSocket reconnection** - Fixed "Failed to reconnect" errors
- ✅ **Message responses** - Fixed OpenAI API v1.x integration
- ✅ **Permission checks** - Fixed user ID validation in 9 endpoints
- ✅ **Conversation deletion** - Added missing DELETE endpoint
- ✅ **Type checking** - Fixed hash-based ID type hints
- ✅ **Analytics dashboard loading** - Fixed JWT verification and service communication
- ✅ **Database path issues** - Implemented absolute paths for all databases
- ✅ **Cross-platform script support** - Added Windows and Linux/Mac script organization

See [CHANGELOG.md](./CHANGELOG.md) for detailed fix information.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React for the UI library
- OpenAI for AI capabilities
- Docker for containerization

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at /docs endpoints

---

**Built with ❤️ using React, FastAPI, and OpenAI**
