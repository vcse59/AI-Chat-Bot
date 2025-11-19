# Quick Start Guide - Local Development

This guide covers both **automated setup** (using scripts) and **manual setup** (step-by-step) for running ConvoAI on your host machine.

---

## 🚀 Automated Setup (Using Scripts)

### Windows

```cmd
# 1. Setup virtual environments (first time only)
scripts\windows\setup-venv.bat

# 2. Create admin user (first time only)
scripts\windows\setup-admin.bat

# 3. Start all services
scripts\windows\start-all-services.bat

# 4. Access the application
Open browser: http://localhost:3000
Login: admin / admin123
```

### Linux/Mac

```bash
# 0. Make scripts executable (first time only)
chmod +x scripts/linux-mac/*.sh

# 1. Setup virtual environments (first time only)
./scripts/linux-mac/setup-venv.sh

# 2. Create admin user (first time only)
./scripts/linux-mac/setup-admin.sh

# 3. Start all services
./scripts/linux-mac/start-all-services.sh

# 4. Access the application
Open browser: http://localhost:3000
Login: admin / admin123
```

---

## 🔧 Manual Setup (Step-by-Step)

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenAI API Key
- 5 terminal windows/tabs

### Step 1: Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd AI-Chat-Bot

# Create .env file in project root
cp .env.example .env

# Edit .env and set:
#   AUTH_SECRET_KEY=<generate-a-secure-random-key>
#   OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Step 2: Auth Service Setup (Terminal 1)

```bash
# Navigate to auth-service
cd auth-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -e .

# Create .env file (optional - will use root .env)
# Or copy shared secret:
# echo "AUTH_SECRET_KEY=<your-key>" > .env

# Start auth service
uvicorn auth_server.main:app --host 0.0.0.0 --port 8001 --reload
```

**Verify:** Open http://localhost:8001/docs - should see Swagger UI

### Step 3: Create Admin User (Terminal 2 - Temporary)

```bash
# Navigate to auth-service
cd auth-service

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Create admin user
python -c "
import sys
sys.path.insert(0, '.')
from auth_server.database.db import init_db
from auth_server.models.user import User
from auth_server.models.role import Role
from auth_server.models.user_role import UserRole
from passlib.context import CryptContext

init_db()
from auth_server.database.db import SessionLocal

db = SessionLocal()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Create admin role
admin_role = db.query(Role).filter(Role.name == 'admin').first()
if not admin_role:
    admin_role = Role(name='admin', description='Administrator')
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

# Create admin user
admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    admin = User(
        username='admin',
        email='admin@example.com',
        hashed_password=pwd_context.hash('admin123'),
        full_name='Admin User',
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()
    print('✅ Admin user created: admin / admin123')
else:
    print('ℹ️  Admin user already exists')

db.close()
"

# Close this terminal after admin is created
```

### Step 4: Chat Service Setup (Terminal 2)

```bash
# Navigate to chat-service
cd chat-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
# echo "OPENAI_API_KEY=sk-your-key" > .env
# echo "AUTH_SECRET_KEY=<your-key>" >> .env

# Start chat service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Verify:** Open http://localhost:8000/docs - should see Swagger UI

### Step 5: Analytics Service Setup (Terminal 3)

```bash
# Navigate to analytics-service
cd analytics-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
# echo "AUTH_SECRET_KEY=<your-key>" > .env

# Start analytics service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Verify:** Open http://localhost:8002/docs - should see Swagger UI

### Step 6: Timezone MCP Server Setup (Terminal 4)

```bash
# Navigate to timezone-mcp-server
cd timezone-mcp-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start MCP server
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Verify:** Open http://localhost:8003/health - should return status

### Step 7: Frontend Setup (Terminal 5)

```bash
# Navigate to frontend
cd chat-frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env (defaults should work):
#   REACT_APP_AUTH_API_URL=http://localhost:8001
#   REACT_APP_CHAT_API_URL=http://localhost:8000
#   REACT_APP_ANALYTICS_API_URL=http://localhost:8002
#   REACT_APP_WS_URL=ws://localhost:8000

# Start frontend
npm start
```

**Verify:** Browser should automatically open to http://localhost:3000

---

## ✅ Verification

### Service Health Checks

```bash
# Auth Service
curl http://localhost:8001/health

# Chat Service  
curl http://localhost:8000/health

# Analytics Service
curl http://localhost:8002/health

# Timezone MCP Server
curl http://localhost:8003/health
```

### Test Login

1. Navigate to http://localhost:3000
2. Login with: `admin` / `admin123`
3. Should see chat interface

### Test Chat

1. Create a new conversation
2. Send a message
3. Should receive AI response

### Test MCP Integration

1. Click "🔌 MCP Servers" button
2. Add new MCP server:
   - Name: Timezone Server
   - Description: Get current time in any timezone
   - Server URL: `http://localhost:8003/mcp`
   - Active: ✓
3. Ask: "What time is it in Tokyo?"
4. Should receive current time in Tokyo

---

## 🛑 Stopping Services

### Automated (Using Scripts)

**Windows:**
```cmd
scripts\windows\stop-all-services.bat
```

**Linux/Mac:**
```bash
./scripts/linux-mac/stop-all-services.sh
```

### Manual
Simply press `Ctrl+C` in each terminal window running a service.

---

## 🔄 Restarting Services

### After Code Changes

**Backend Services** (Auth, Chat, Analytics, MCP):
- If running with `--reload` flag, changes are automatically detected
- No restart needed for code changes
- Database schema changes may require restart

**Frontend**:
- Changes are automatically detected by React dev server
- Browser will hot-reload

### Full Restart

Stop all services and start them again following the setup steps.

---

## 📍 Service URLs

| Service | URL | API Docs |
|---------|-----|----------|
| Frontend | http://localhost:3000 | - |
| Auth Service | http://localhost:8001 | /docs |
| Chat Service | http://localhost:8000 | /docs |
| Analytics Service | http://localhost:8002 | /docs |
| Timezone MCP Server | http://localhost:8003 | /health |

---

## 🔐 Managing Admin Users

### Create/Update Admin User

**Windows:**
```cmd
scripts\windows\setup-admin.bat
```

**Linux/Mac:**
```bash
./scripts/linux-mac/setup-admin.sh
```

### List All Admins

**Windows:**
```cmd
scripts\windows\list-admins.bat
```

**Linux/Mac:**
```bash
./scripts/linux-mac/list-admins.sh
```

---

## 🐛 Common Issues

### Port Already in Use

```bash
# Find process using port (example: port 8000)
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process-id> /F

# Linux/Mac:
lsof -i :8000
kill -9 <process-id>

# Or use different port:
uvicorn main:app --port 8010
```

### Import Errors

```bash
# Ensure virtual environment is activated
# Check with:
which python  # Linux/Mac
where python  # Windows

# Should point to venv/bin/python or venv\Scripts\python.exe

# Reinstall dependencies:
pip install -r requirements.txt
```

### Database Errors

```bash
# Delete and recreate databases
rm auth-service/auth.db
rm chat-service/data/chatbot.db
rm analytics-service/data/analytics.db

# Restart services - databases will be recreated
```

### Frontend Not Connecting

```bash
# Check .env file in chat-frontend
cat chat-frontend/.env  # Linux/Mac
type chat-frontend\.env  # Windows

# Verify URLs match running services:
REACT_APP_AUTH_API_URL=http://localhost:8001
REACT_APP_CHAT_API_URL=http://localhost:8000
REACT_APP_ANALYTICS_API_URL=http://localhost:8002
REACT_APP_WS_URL=ws://localhost:8000

# Restart frontend after .env changes
```

### OpenAI API Errors

```bash
# Verify API key is set
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows

# Test API key:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-key-here"
```

### MCP Server Connection Issues

When running on host machine, use `localhost`:
```
Server URL: http://localhost:8003/mcp
```

When running in Docker, use service name:
```
Server URL: http://timezone-mcp-server:8003/mcp
```

---

## 📚 Additional Resources

- [Main README](../README.md) - Complete project documentation
- [Scripts Documentation](../scripts/README.md) - All available scripts
- [Testing Guide](../tests/README.md) - Running tests
- [MCP Implementation](../MCP_README.md) - MCP integration details
- [Analytics Guide](./ANALYTICS_GUIDE.md) - Analytics features

---

## 🔄 Environment Configuration

### Root .env (Shared)
Located at project root, contains shared secrets:
```env
AUTH_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-key-here
```

### Service-Specific .env Files
Each service can have its own `.env` for service-specific config:
- `auth-service/.env`
- `chat-service/.env`
- `analytics-service/.env`
- `timezone-mcp-server/.env`
- `chat-frontend/.env`

Services automatically load from root `.env` if service `.env` doesn't exist.

---

## 💡 Tips

### Use Multiple Terminals Efficiently

- Use terminal multiplexers like `tmux` (Linux/Mac) or `Windows Terminal` with tabs
- Name each terminal tab with the service name for easy identification
- Consider using VS Code's integrated terminal with split panes

### Quick Commands

```bash
# Check if all services are running
curl -s http://localhost:8001/health && echo "✅ Auth" || echo "❌ Auth"
curl -s http://localhost:8000/health && echo "✅ Chat" || echo "❌ Chat"
curl -s http://localhost:8002/health && echo "✅ Analytics" || echo "❌ Analytics"
curl -s http://localhost:8003/health && echo "✅ MCP" || echo "❌ MCP"
```

### Development Workflow

1. Start backend services first (Auth → Chat → Analytics → MCP)
2. Wait for each to fully start before starting the next
3. Start frontend last
4. Make code changes - services auto-reload with `--reload` flag
5. Check logs in each terminal for errors

---

## 🎯 Next Steps

Once you have everything running:

1. **Explore the Chat Interface**
   - Create conversations
   - Send messages and get AI responses
   - Try different conversation types

2. **Register MCP Servers**
   - Click "🔌 MCP Servers" button
   - Add the timezone server
   - Test with timezone questions

3. **View Analytics** (Admin only)
   - Click analytics icon in sidebar
   - View user activity and metrics
   - Monitor token usage

4. **Create Additional Users**
   - Register new users via frontend
   - Test multi-user scenarios
   - Assign different roles

5. **Customize and Extend**
   - Modify frontend components
   - Add new API endpoints
   - Create custom MCP servers
   - Integrate additional AI models

---

**Built with ❤️ using React, FastAPI, and OpenAI**
- See `README.md` for full documentation
