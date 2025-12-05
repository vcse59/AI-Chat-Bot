# Quick Start: MCP Server Management

## Setup (One-time)

```bash
# 1. Initialize the database
cd chat-service
python init_mcp_db.py

# 2. Start all services
cd ..
docker-compose up -d

# Or start individually:
# Terminal 1: Auth Service
cd auth-service
uvicorn auth_server.main:app --port 8001

# Terminal 2: Chat Service  
cd chat-service
uvicorn main:app --port 8000

# Terminal 3: Frontend
cd chat-frontend
npm start

# Terminal 4: Timezone MCP Server (example)
cd timezone-mcp-server
python server.py
```

## Using the Feature

### Via Web UI:

1. **Open**: http://localhost:3000
2. **Login**: Use your credentials
3. **Click**: "🔌 MCP Servers" button in header
4. **Add Server**:
   - Click "+ Add MCP Server"
   - Fill in the form:
     * Name: "Timezone MCP Server"
     * Description: "Provides timezone operations"
     * Server URL: "http://localhost:8003"
     * API Key: (leave empty if not needed)
     * Active: ✓ checked
   - Click "Create Server"

5. **Manage Servers**:
   - View all your servers in a grid
   - Edit: Click "Edit" button
   - Delete: Click "Delete" button
   - Toggle status: Edit and check/uncheck "Active"

### Via API:

```bash
# Get your token first by logging in
TOKEN="your_jwt_token_here"

# Create MCP Server
curl -X POST http://localhost:8000/api/v1/mcp-servers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Timezone MCP Server",
    "server_url": "http://localhost:8003",
    "is_active": true
  }'

# List your servers
curl http://localhost:8000/api/v1/mcp-servers/ \
  -H "Authorization: Bearer $TOKEN"

# Get specific server
curl http://localhost:8000/api/v1/mcp-servers/SERVER_ID \
  -H "Authorization: Bearer $TOKEN"

# Update server
curl -X PUT http://localhost:8000/api/v1/mcp-servers/SERVER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'

# Delete server
curl -X DELETE http://localhost:8000/api/v1/mcp-servers/SERVER_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Example: Register Timezone MCP Server

1. Start the timezone MCP server:
   ```bash
   cd timezone-mcp-server
   python server.py
   ```

2. In the web UI (http://localhost:3000):
   - Click "🔌 MCP Servers"
   - Click "+ Add MCP Server"
   - Enter:
     * Name: **Timezone MCP Server**
     * Description: **Provides timezone information and conversions**
     * Server URL: **http://localhost:8003**
     * Active: **✓** (checked)
   - Click "Create Server"

3. You should see your server in the list!

## Troubleshooting

### Database Error
```bash
cd chat-service
python init_mcp_db.py
```

### Can't See MCP Button
- Make sure you're logged in
- Refresh the page
- Check browser console for errors

### API Returns 401
- Your token expired, log in again
- Check auth-service is running on port 8001

### API Returns 403
- You don't own that server
- Or you're not an admin

### Server List Empty
- Create your first server
- Check network tab for API errors
- Verify chat-service is running on port 8000

## Port Reference

- **3000**: React Frontend
- **8000**: Chat Service (MCP Server APIs)
- **8001**: Auth Service
- **8002**: Analytics Service
- **8003**: Timezone MCP Server (example)

## Quick Test

```bash
# 1. Check services are running
curl http://localhost:8001/health  # Auth
curl http://localhost:8000/health  # Chat
curl http://localhost:3000         # Frontend

# 2. Login to get token
curl -X POST http://localhost:8001/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_USERNAME&password=YOUR_PASSWORD"

# 3. Test MCP endpoint
curl http://localhost:8000/api/v1/mcp-servers/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Next Steps

- Add more MCP servers
- Integrate with chat conversations
- Explore MCP server tools
- Check analytics (if admin)

## Documentation

- Full docs: `docs/MCP_SERVER_MANAGEMENT.md`
- Implementation details: `docs/MCP_IMPLEMENTATION_SUMMARY.md`
- Main README: `README.md`

## Support

If you encounter issues:
1. Check all services are running
2. Verify ports are not in use
3. Check logs: `docker-compose logs -f`
4. Review browser console
5. Check database exists: `ls chat-service/data/`

---

**That's it! You're ready to manage MCP servers in ConvoAI! 🎉**

---

**Last Updated:** December 5, 2025  
**Version:** 3.0.0
