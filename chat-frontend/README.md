# Chat Frontend

React-based chat application with OAuth 2.0 authentication, real-time messaging, and analytics dashboard.

## Features

- 🔐 **OAuth 2.0 Authentication**: Secure login/registration using JWT tokens
- 💬 **Real-time Chat**: WebSocket-based messaging for instant communication
- 📝 **Conversation Management**: Create, view, and delete conversations
- 📊 **Analytics Dashboard**: View conversation metrics and statistics
- 🎨 **Modern UI**: Responsive design with gradient themes
- 🔄 **Auto-reconnect**: Automatic WebSocket reconnection on connection loss
- 📱 **Mobile Responsive**: Works seamlessly on all device sizes

## Architecture

### Services Integration

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│  React Frontend │─────▶│  Auth Server (8001)  │      │                 │
│    (Port 3000)  │      │  - OAuth 2.0         │      │  ChatBot API    │
│                 │      │  - User Management   │      │  (Port 8000)    │
│  - Login/Register│      │  - JWT Tokens       │      │                 │
│  - Chat UI      │      └──────────────────────┘      │  - Conversations│
│  - WebSocket    │                                     │  - Messages     │
│  - Analytics    │──────────────────────────────────▶ │  - WebSocket    │
│                 │        Bearer Token Auth            │  - OpenAI       │
└─────────────────┘                                     └─────────────────┘
         │                                                        │
         │               ┌──────────────────────┐                │
         └──────────────▶│  Analytics (8002)    │◀───────────────┘
                         │  - Metrics           │
                         │  - Statistics        │
                         │  - Conversations     │
                         └──────────────────────┘
```

### Authentication Flow

1. User registers/logs in via Auth Server
2. Auth Server returns JWT access token
3. Frontend stores token in localStorage
4. All API requests include `Authorization: Bearer <token>` header
5. WebSocket connects with `?token=<token>` query parameter

## Project Structure

```
chat-frontend/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/             # React components
│   │   ├── ChatWindow.js       # Main chat interface
│   │   ├── ConversationList.js # Sidebar with conversations
│   │   ├── MessageList.js      # Message display
│   │   └── MessageInput.js     # Message input field
│   ├── contexts/
│   │   └── AuthContext.js      # Authentication state management
│   ├── hooks/
│   │   ├── useChat.js          # Chat logic and WebSocket
│   │   └── useConversations.js # Conversation management
│   ├── pages/
│   │   ├── Login.js            # Login page
│   │   ├── Register.js         # Registration page
│   │   └── ChatPage.js         # Main chat page
│   ├── services/
│   │   ├── authService.js      # Auth API client
│   │   ├── chatService.js      # Chat API client
│   │   └── websocketService.js # WebSocket manager
│   ├── App.js                  # Main app with routing
│   └── index.js                # App entry point
├── Dockerfile                  # Production build
├── nginx.conf                  # Nginx configuration
├── package.json                # Dependencies
└── .env                        # Environment variables
```

## Environment Variables

Create a `.env` file in the `chat-frontend` directory:

```env
REACT_APP_AUTH_API_URL=http://localhost:8001
REACT_APP_CHAT_API_URL=http://localhost:8000
REACT_APP_ANALYTICS_API_URL=http://localhost:8002
REACT_APP_WS_URL=ws://localhost:8000
```

## Installation & Development

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend services running (auth, chat, analytics)

### Install Dependencies

```bash
cd chat-frontend
npm install
```

### Run Development Server

```bash
npm start
```

The app will run on `http://localhost:3000`

**Using Platform Scripts** (from project root):

**Windows:**
```cmd
scripts\windows\start-frontend.bat
```

**Linux/Mac:**
```bash
scripts/linux-mac/start-frontend.sh
```

### Build for Production

```bash
npm run build
```

## Docker Deployment

### Build Image

```bash
docker build -t chat-frontend .
```

### Run Container

```bash
docker run -p 3000:3000 chat-frontend
```

### Docker Compose

The app is included in the main `docker-compose.yml`:

```yaml
chat-frontend:
  build: ./chat-frontend
  ports:
    - "3000:3000"
  environment:
    - REACT_APP_AUTH_API_URL=http://localhost:8001
    - REACT_APP_CHAT_API_URL=http://localhost:8000
    - REACT_APP_WS_URL=ws://localhost:8000
```

## Usage Guide

### 1. Register a New Account

1. Navigate to `http://localhost:3000/register`
2. Fill in username, email, password
3. Click "Create Account"
4. Redirected to login page

### 2. Login

1. Navigate to `http://localhost:3000/login`
2. Enter username and password
3. Click "Sign In"
4. Redirected to chat interface

### 3. Create a Conversation

1. Click the ➕ button in the sidebar
2. Enter conversation title
3. Click "Create"

### 4. Send Messages

1. Select a conversation from the sidebar
2. Type message in the input field
3. Press Enter or click 📤 to send
4. Messages appear in real-time via WebSocket

### 5. Delete a Conversation

1. Hover over a conversation in the sidebar
2. Click the 🗑️ button
3. Confirm deletion

## API Integration

### Authentication Service (Port 8001)

**Register User**
```javascript
POST /users/
Body: {
  "username": "john",
  "email": "john@example.com",
  "password": "secret123",
  "full_name": "John Doe"
}
```

**Login**
```javascript
POST /auth/token
Body: username=john&password=secret123
Response: {
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

### Chat Service (Port 8000)

All endpoints require `Authorization: Bearer <token>` header.

**Get Conversations**
```javascript
GET /conversations/
Headers: { Authorization: "Bearer <token>" }
```

**Create Conversation**
```javascript
POST /conversations/
Headers: { Authorization: "Bearer <token>" }
Body: { "title": "My Conversation" }
```

**Get Messages**
```javascript
GET /conversations/{conversation_id}/messages
Headers: { Authorization: "Bearer <token>" }
```

**Send Message**
```javascript
POST /conversations/{conversation_id}/messages
Headers: { Authorization: "Bearer <token>" }
Body: {
  "conversation_id": "abc123xyz",
  "role": "user",
  "content": "Hello!"
}
```

**Delete Conversation**
```javascript
DELETE /api/v1/users/{username}/conversations/{conversation_id}
Headers: { Authorization: "Bearer <token>" }
```

**WebSocket Connection**
```javascript
ws://localhost:8000/ws/{conversation_id}?token=<jwt_token>
```

### Analytics Service (Port 8002)

All endpoints require `Authorization: Bearer <token>` header.

**Get Analytics Summary**
```javascript
GET /analytics/summary
Headers: { Authorization: "Bearer <token>" }
```

**Get Conversation Metrics**
```javascript
GET /analytics/conversations
Headers: { Authorization: "Bearer <token>" }
```

**Get User Activity**
```javascript
GET /analytics/users/{user_id}/activity
Headers: { Authorization: "Bearer <token>" }
```

## Features Implementation

### OAuth 2.0 Security

- JWT tokens stored in localStorage
- Automatic token inclusion in API requests
- Token validation on protected routes
- Auto-logout on 401 Unauthorized

### WebSocket Real-time Messaging

- Automatic connection on conversation select
- Auto-reconnection with configurable retry attempts (max 5)
- Proper cleanup when switching conversations
- Connection status indicator
- Fallback to HTTP API if WebSocket fails

### State Management

- React Context API for authentication
- Custom hooks for chat and conversations
- Optimistic UI updates
- Error handling and recovery

### Responsive Design

- Mobile-first approach
- Flexbox and CSS Grid layouts
- Touch-friendly interface
- Gradient color schemes

## Troubleshooting

### CORS Issues

If you encounter CORS errors, ensure the backend services have CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### WebSocket Connection Failed

1. Check if chatbot service is running on port 8000
2. Verify token is valid and not expired
3. Check browser console for error messages
4. Ensure WebSocket URL uses `ws://` not `wss://` for local development
5. Verify conversation exists and you have access to it

### Conversation Deletion Not Working

If deletion fails with "Not Found":

1. Ensure you're logged in with a valid token
2. Verify you own the conversation you're trying to delete
3. Check browser console for specific error messages
4. Ensure backend DELETE endpoint is available (added in recent update)

### WebSocket Reconnection Issues

If you see "Failed to reconnect after maximum attempts":

1. This has been fixed in the latest version
2. Clear browser cache and reload the page
3. The reconnection logic now properly handles conversation switching
4. Max reconnection attempts is 5, then resets for future connections

### Authentication Errors

1. Clear localStorage and try logging in again
2. Verify auth-server is running on port 8001
3. Check network tab for API responses
4. Ensure username/password are correct

## Development Tips

### Hot Reload

React's development server includes hot module replacement. Changes are reflected immediately.

### Debugging

Use React DevTools extension for Chrome/Firefox to inspect component state and props.

### API Testing

Use the browser's Network tab to inspect API requests and responses.

## Production Considerations

1. **Environment Variables**: Use production URLs in `.env`
2. **HTTPS**: Enable SSL/TLS for production
3. **Security Headers**: Already configured in nginx.conf
4. **Asset Optimization**: Build includes minification and compression
5. **Caching Strategy**: Static assets cached for 1 year

## License

MIT License - See main project LICENSE file
