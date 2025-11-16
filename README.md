# Open ChatBot - Intelligent Conversation Platform

A production-ready, full-stack chatbot platform featuring a React frontend, OAuth 2.0 authentication, real-time WebSocket communication, and OpenAI integration. Built with React and FastAPI for a complete microservices solution.

## 🌟 Overview

This platform consists of three main components working together to provide a secure, intelligent chatbot experience:

1. **React Chat Frontend** (Port 3000) - Modern, responsive web UI with real-time messaging
2. **Authorization Server** (Port 8001) - OAuth 2.0 authentication and role-based access control
3. **ChatBot Service** (Port 8000) - AI-powered conversations with OpenAI and WebSocket support

All services are containerized with Docker and orchestrated using Docker Compose for easy deployment.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│                    http://localhost:3000                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                    React Chat Frontend                          │
│                      (Port 3000)                                │
│  - Login/Register UI         - Protected Routes                │
│  - Chat Interface            - State Management                 │
│  - WebSocket Client          - OAuth 2.0 Integration            │
└──────┬─────────────────────────────────────────────┬───────────┘
       │                                             │
       │ HTTP POST /auth/token                       │ HTTP + Bearer Token
       │ HTTP POST /users/                           │ WebSocket + Token
       │                                             │
       ▼                                             ▼
┌─────────────────────────┐           ┌────────────────────────────┐
│  Authorization Server   │           │    ChatBot Service         │
│      (Port 8001)        │◄──────────│      (Port 8000)           │
│                         │  Verify   │                            │
│  - User Management      │  Token    │  - Conversation CRUD       │
│  - JWT Token Service    │           │  - Message Management      │
│  - RBAC (Roles)         │           │  - WebSocket Handler       │
│  - Password Hashing     │           │  - OpenAI Integration      │
│                         │           │  - OAuth Middleware        │
└──────────┬──────────────┘           └────────────┬───────────────┘
           │                                       │
           ▼                                       ▼
    ┌─────────────┐                        ┌──────────────┐
    │  auth.db    │                        │conversations.│
    │  (SQLite)   │                        │   db         │
    │             │                        │  (SQLite)    │
    │ - users     │                        │              │
    │ - roles     │                        │- conversations
    │ - user_roles│                        │- messages    │
    └─────────────┘                        └──────────────┘
```

## ✨ Key Features

### Frontend (React)
- 🎨 **Modern UI**: Gradient themes, responsive design, smooth animations
- 🔐 **Secure Authentication**: OAuth 2.0 with JWT tokens
- 💬 **Real-time Chat**: WebSocket-based instant messaging
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
- 🏥 **Health Checks**: Service monitoring endpoints

## 📦 Project Structure

```
Open-ChatBot/
├── chat-frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/           # UI components
│   │   │   ├── ChatWindow.js
│   │   │   ├── ConversationList.js
│   │   │   ├── MessageList.js
│   │   │   └── MessageInput.js
│   │   ├── contexts/
│   │   │   └── AuthContext.js    # Auth state management
│   │   ├── hooks/
│   │   │   ├── useChat.js
│   │   │   └── useConversations.js
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   └── ChatPage.js
│   │   ├── services/
│   │   │   ├── authService.js    # Auth API client
│   │   │   ├── chatService.js    # Chat API client
│   │   │   └── websocketService.js
│   │   ├── App.js                # Main app with routing
│   │   └── index.js
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── authentication-authorization/  # Auth server
│   └── Authentication-Authorization/
│       ├── auth_server/
│       │   ├── main.py           # FastAPI app
│       │   ├── database/         # DB configuration
│       │   ├── models/           # SQLAlchemy models
│       │   ├── routers/          # API routes
│       │   ├── schemas/          # Pydantic schemas
│       │   └── security/         # Auth logic
│       ├── tests/
│       └── Dockerfile
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
│   ├── services/
│   │   └── openai_service.py
│   ├── utilities/
│   │   └── hash_utils.py         # ID generation
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml             # Orchestration
├── .env                           # Environment variables
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

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- OpenAI API Key

### 1. Clone Repository

```bash
git clone <repository-url>
cd Open-ChatBot
```

### 2. Configure Environment

Create/update `.env` file in the project root:

```env
# Authentication Secret Key (IMPORTANT: Change in production!)
AUTH_SECRET_KEY=your-secure-secret-key-at-least-32-characters-long

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Start All Services

```bash
docker-compose up --build
```

This will start:
- React Frontend: `http://localhost:3000`
- Auth Server: `http://localhost:8001`
- ChatBot Service: `http://localhost:8000`

### 4. Access the Application

1. Open browser to `http://localhost:3000`
2. Register a new account
3. Login with your credentials
4. Start chatting!

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

## 🔧 Development

### Frontend Development

```bash
cd chat-frontend
npm install
npm start
```

Runs on `http://localhost:3000` with hot reload.

### Backend Development

**Auth Server:**
```bash
cd authentication-authorization/Authentication-Authorization
pip install -r requirements.txt
uvicorn auth_server.main:app --reload --port 8001
```

**ChatBot Service:**
```bash
cd openai_web_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

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

**React Frontend:**
```bash
curl http://localhost:3000
```

## 🛠️ Troubleshooting

### CORS Issues

If you see CORS errors in browser console:

1. Verify backend services have CORS enabled
2. Check allowed origins in FastAPI middleware
3. Ensure requests include proper headers

### WebSocket Connection Failed

1. Check chatbot service is running: `docker ps`
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

### Authentication Errors

1. Clear browser localStorage: `localStorage.clear()`
2. Verify auth-server is running
3. Check network tab for API responses
4. Ensure .env has correct AUTH_SECRET_KEY

### Database Issues

Reset databases:
```bash
docker-compose down -v
docker-compose up --build
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

- [Frontend README](./chat-frontend/README.md)
- [Auth Server README](./authentication-authorization/Authentication-Authorization/README.md)
- [ChatBot Service README](./openai_web_service/README.md)
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
