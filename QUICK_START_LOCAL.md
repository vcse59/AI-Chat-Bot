# Quick Start Guide - Local Development

Choose your platform:

## Windows

```cmd
# 1. Setup virtual environments (first time only)
scripts\windows\setup-venv.bat

# 2. Start all services
scripts\windows\start-all-services.bat

# 3. Access the application
Open browser: http://localhost:3000
Login: admin / admin123
```

## Linux/Mac

```bash
# 0. Make scripts executable (first time only)
chmod +x scripts/linux-mac/*.sh

# 1. Setup virtual environments (first time only)
./scripts/linux-mac/setup-venv.sh

# 2. Start all services
./scripts/linux-mac/start-all-services.sh

# 3. Access the application
Open browser: http://localhost:3000
Login: admin / admin123
```

## Service URLs

- **Frontend:** http://localhost:3000
- **Chat API:** http://localhost:8000/docs
- **Auth API:** http://localhost:8001/docs
- **Analytics API:** http://localhost:8002/docs

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

## Stopping Services

**Windows:**
```cmd
scripts\windows\stop-all-services.bat
```

**Linux/Mac:**
```bash
./scripts/linux-mac/stop-all-services.sh
```

## Managing Admin Users

**Windows:**
```cmd
# Create/update admin user
scripts\windows\setup-admin.bat

# List all admins
scripts\windows\list-admins.bat
```

**Linux/Mac:**
```bash
# Create/update admin user
./scripts/linux-mac/setup-admin.sh

# List all admins
./scripts/linux-mac/list-admins.sh
```

## More Information

- See `scripts/README.md` for all available scripts
- See `README.md` for full documentation
