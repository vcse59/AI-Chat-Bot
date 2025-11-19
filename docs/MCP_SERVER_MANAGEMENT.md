# MCP Server Management Feature

This feature allows users to register and manage MCP (Model Context Protocol) servers in the ConvoAI chat application.

## Features

### Backend (chat-service)

1. **New API Endpoints** (`/api/v1/mcp-servers/`)
   - `POST /mcp-servers/` - Create a new MCP server
   - `GET /mcp-servers/` - List user's MCP servers
   - `GET /mcp-servers/{server_id}` - Get specific MCP server
   - `PUT /mcp-servers/{server_id}` - Update MCP server
   - `DELETE /mcp-servers/{server_id}` - Delete MCP server
   - `GET /admin/mcp-servers/` - List all MCP servers (Admin only)

2. **Authentication & Authorization**
   - All endpoints require valid JWT token
   - Users can only manage their own MCP servers
   - Admin users can view all MCP servers
   - Auth-service integration for token verification

3. **Database Model**
   - MCP servers stored with hash-based IDs
   - Links to user accounts
   - Supports server URL, API key, and custom configuration
   - Active/inactive status tracking

### Frontend (chat-frontend)

1. **MCP Server Manager Component**
   - User-friendly interface for managing MCP servers
   - Add/Edit/Delete operations
   - Server status indicators (Active/Inactive)
   - Form validation
   - Responsive grid layout

2. **Integration with Chat Page**
   - "🔌 MCP Servers" button in header
   - Toggle between chat view and MCP server management
   - Available to all authenticated users

## Setup Instructions

### 1. Database Migration

Run the database initialization script to create the mcp_servers table:

```bash
cd chat-service
python init_mcp_db.py
```

Or use Alembic migration:

```bash
cd chat-service
alembic upgrade head
```

### 2. Start Services

Make sure all services are running:

```bash
# Using Docker Compose
docker-compose up -d

# Or start individually
cd auth-service && uvicorn auth_server.main:app --port 8001
cd chat-service && uvicorn main:app --port 8000
cd chat-frontend && npm start
```

### 3. Access MCP Server Management

1. Log in to the chat application
2. Click the "🔌 MCP Servers" button in the header
3. Add your first MCP server:
   - Name: e.g., "Timezone MCP Server"
   - Description: Optional description
   - Server URL: e.g., "http://localhost:8003"
   - API Key: Optional (if your MCP server requires authentication)
   - Active: Check to enable the server

## API Usage Examples

### Create MCP Server

```bash
curl -X POST http://localhost:8000/api/v1/mcp-servers/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Timezone MCP Server",
    "description": "MCP server for timezone operations",
    "server_url": "http://localhost:8003",
    "api_key": "optional-api-key",
    "is_active": true
  }'
```

### List User's MCP Servers

```bash
curl http://localhost:8000/api/v1/mcp-servers/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update MCP Server

```bash
curl -X PUT http://localhost:8000/api/v1/mcp-servers/SERVER_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

### Delete MCP Server

```bash
curl -X DELETE http://localhost:8000/api/v1/mcp-servers/SERVER_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## File Changes

### Backend Files
- `chat-service/engine/models.py` - Added MCPServer model
- `chat-service/engine/schemas.py` - Added MCP server schemas
- `chat-service/engine/mcp_server_crud.py` - MCP server CRUD operations
- `chat-service/api/routes.py` - Added MCP server endpoints
- `chat-service/security/oauth.py` - Enhanced CurrentUser with token
- `chat-service/init_mcp_db.py` - Database initialization script
- `chat-service/alembic/versions/add_mcp_servers.py` - Migration script

### Frontend Files
- `chat-frontend/src/services/mcpServerService.js` - MCP server API client
- `chat-frontend/src/components/MCPServerManager.js` - Management UI component
- `chat-frontend/src/components/MCPServerManager.css` - Component styling
- `chat-frontend/src/pages/ChatPage.js` - Integrated MCP server button
- `chat-frontend/src/pages/ChatPage.css` - Added MCP button styling

## Security Features

1. **JWT Authentication**
   - All endpoints protected by JWT tokens
   - Token verified with auth-service

2. **Authorization**
   - Users can only access their own MCP servers
   - Admin users have full access

3. **Data Validation**
   - Input validation on both frontend and backend
   - URL validation for server endpoints
   - Required field validation

4. **API Key Protection**
   - API keys stored securely
   - Masked in UI (shown as ••••••••)

## Testing

### Test MCP Server Management

1. **Create a server:**
   - Fill in all required fields
   - Click "Create Server"
   - Verify server appears in the list

2. **Edit a server:**
   - Click "Edit" on a server card
   - Modify fields
   - Click "Update Server"

3. **Delete a server:**
   - Click "Delete" on a server card
   - Confirm deletion
   - Verify server is removed

4. **Toggle active status:**
   - Edit a server
   - Toggle the "Active" checkbox
   - Inactive servers appear with reduced opacity

## Integration with Timezone MCP Server

The timezone-mcp-server created earlier can now be registered:

1. Start the timezone-mcp-server:
   ```bash
   cd timezone-mcp-server
   python server.py
   ```

2. Register it in the UI:
   - Name: "Timezone MCP Server"
   - Server URL: "http://localhost:8003"
   - Description: "Provides timezone information and conversions"

3. Use it in your chat application (future integration)

## Future Enhancements

- [ ] MCP server health check/ping functionality
- [ ] Integration with chat conversations
- [ ] MCP tool discovery and listing
- [ ] Server statistics and usage tracking
- [ ] Bulk operations (enable/disable multiple servers)
- [ ] Server templates for common MCP servers
- [ ] Import/Export server configurations
- [ ] Server connection testing before saving

## Troubleshooting

### Database Issues
- Run `python init_mcp_db.py` to create tables
- Check database file permissions
- Verify DATABASE_URL environment variable

### Authentication Issues
- Verify JWT token is valid
- Check auth-service is running
- Ensure AUTH_SECRET_KEY matches across services

### Frontend Issues
- Clear browser cache
- Check browser console for errors
- Verify REACT_APP_CHAT_API_URL is set correctly

## Support

For issues or questions:
1. Check the main README.md
2. Review server logs
3. Check database connectivity
4. Verify all services are running
