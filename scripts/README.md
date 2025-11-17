# Service Scripts

This folder contains platform-specific scripts to run all services on the host machine using Python virtual environments.

## Directory Structure

```
scripts/
├── windows/          # Windows scripts (.bat files)
├── linux-mac/        # Linux/Mac scripts (.sh files)
└── README.md         # This file
```

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm

## Platform-Specific Usage

### Windows

All scripts are in `scripts\windows\` with `.bat` extension.

**Setup (First Time):**
```cmd
scripts\windows\setup-venv.bat
```

**Start All Services:**
```cmd
scripts\windows\start-all-services.bat
```

**Individual Services:**
```cmd
scripts\windows\start-auth-service.bat
scripts\windows\start-chat-service.bat
scripts\windows\start-analytics-service.bat
scripts\windows\start-frontend.bat
```

**Stop All Services:**
```cmd
scripts\windows\stop-all-services.bat
```

**Admin Management:**
```cmd
scripts\windows\setup-admin.bat
scripts\windows\list-admins.bat
```

**Run Tests:**
```cmd
scripts\windows\run-tests.bat
```

**Check Services:**
```cmd
scripts\windows\check-services.bat
```

### Linux/Mac

All scripts are in `scripts/linux-mac/` with `.sh` extension.

**First Time Setup - Make scripts executable:**
```bash
chmod +x scripts/linux-mac/*.sh
```

**Setup (First Time):**
```bash
./scripts/linux-mac/setup-venv.sh
```

**Start All Services:**
```bash
./scripts/linux-mac/start-all-services.sh
```

**Individual Services:**
```bash
./scripts/linux-mac/start-auth-service.sh
./scripts/linux-mac/start-chat-service.sh
./scripts/linux-mac/start-analytics-service.sh
./scripts/linux-mac/start-frontend.sh
```

**Stop All Services:**
```bash
./scripts/linux-mac/stop-all-services.sh
```

**Admin Management:**
```bash
./scripts/linux-mac/setup-admin.sh
./scripts/linux-mac/list-admins.sh
```

**Run Tests:**
```bash
./scripts/linux-mac/run-tests.sh
```

**Check Services:**
```bash
./scripts/linux-mac/check-services.sh
```

## Service URLs

Once running:
- **Frontend:** http://localhost:3000
- **Chat API:** http://localhost:8000
  - Docs: http://localhost:8000/docs
- **Auth API:** http://localhost:8001
  - Docs: http://localhost:8001/docs
- **Analytics API:** http://localhost:8002
  - Docs: http://localhost:8002/docs

## Default Credentials

- **Admin User:**
  - Username: `admin`
  - Password: `admin123`

## Troubleshooting

**Virtual environment not found:**
- Run `scripts\setup-venv.bat` first

**Port already in use:**
- Stop any running Docker containers: `docker compose down`
- Check for other processes using the ports
- Use `netstat -ano | findstr "8000"` to find processes

**OpenAI functionality not working:**
- Make sure `OPENAI_API_KEY` is set in `start-chat-service.bat`

**Frontend not loading:**
- Check that all backend services are running
- Clear browser cache and reload

## Project Structure

```
ConvoAI/
├── auth-service/          # Auth service with venv
│   └── venv/
├── chat-service/    # Chat & Analytics service with venv
│   └── venv/
├── chat-frontend/         # React frontend
│   └── node_modules/
├── tests/                 # Test suite with venv
│   └── venv/
└── scripts/              # All service scripts (this folder)
    ├── setup-venv.bat
    ├── start-all-services.bat
    ├── start-auth-service.bat
    ├── start-chat-service.bat
    ├── start-analytics-service.bat
    ├── start-frontend.bat
    ├── stop-all-services.bat
    └── run-tests.bat
```

