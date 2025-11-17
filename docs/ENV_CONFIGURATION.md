# Environment Configuration Guide

Each service has its own `.env` file for configuration. These files have been created with default values from the parent `.env` file.

## Service Environment Files

### 1. Auth Service (`auth-service/.env`)
**Configuration:**
- `AUTH_SECRET_KEY` - Secret key for JWT signing
- `PORT` - Service port (default: 8001)
- `DATABASE_URL` - Auth database path
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` - Default admin credentials

### 2. Chat Service (`openai_web_service/.env`)
**Configuration:**
- `OPENAI_API_KEY` - Your OpenAI API key ⚠️ **REQUIRED for chat**
- `PORT` - Service port (default: 8000)
- `DATABASE_URL` - Chat database path
- `AUTH_SECRET_KEY` - Same as auth service (for JWT validation)
- `AUTH_SERVICE_URL` - Auth service URL

### 3. Analytics Service (`analytics-service/.env`)
**Configuration:**
- `PORT` - Service port (default: 8002)
- `DATABASE_URL` - Analytics database path
- `AUTH_SECRET_KEY` - Same as auth service (for JWT validation)
- `AUTH_SERVICE_URL` - Auth service URL

### 4. Frontend (`chat-frontend/.env`)
**Configuration:**
- `REACT_APP_AUTH_API_URL` - Auth API endpoint
- `REACT_APP_CHAT_API_URL` - Chat API endpoint
- `REACT_APP_ANALYTICS_API_URL` - Analytics API endpoint

## Important Notes

### OpenAI API Key
The OpenAI API key is already configured in `openai_web_service/.env`. If you need to update it:
1. Get your API key from https://platform.openai.com/api-keys
2. Edit `openai_web_service/.env`
3. Replace the `OPENAI_API_KEY` value
4. Restart the chat service

### Shared Secret Key
The `AUTH_SECRET_KEY` must be the same across:
- `auth-service/.env`
- `openai_web_service/.env`
- `analytics-service/.env`

This ensures JWT tokens work across all services.

## How Scripts Load .env Files

The startup scripts automatically load environment variables from each service's `.env` file:
- `scripts/start-auth-service.bat` → Loads `auth-service/.env`
- `scripts/start-chat-service.bat` → Loads `openai_web_service/.env`
- `scripts/start-analytics-service.bat` → Loads `analytics-service/.env`
- Frontend automatically loads `.env` via React

## Security Notes

⚠️ **DO NOT commit .env files to Git!**
- The `.env` files contain sensitive information (API keys, secrets)
- Add them to `.gitignore`
- For production, use environment variables or secret management

## Customization

To customize any setting:
1. Edit the appropriate `.env` file
2. Save the changes
3. Restart the affected service

Example - Change Chat Service port:
```bash
# Edit openai_web_service/.env
PORT=9000

# Restart service
scripts\start-chat-service.bat
```

## Troubleshooting

**Services can't communicate:**
- Check `AUTH_SERVICE_URL`, `CHAT_SERVICE_URL` point to correct ports
- Ensure all services use `localhost` (not `127.0.0.1` mixed with `localhost`)

**Chat not working:**
- Verify `OPENAI_API_KEY` is set in `openai_web_service/.env`
- Check the OpenAI API key is valid

**Auth errors across services:**
- Verify `AUTH_SECRET_KEY` is identical in all service `.env` files

**Frontend can't connect:**
- Check URLs in `chat-frontend/.env` match your service ports
- Restart frontend after changing `.env`
