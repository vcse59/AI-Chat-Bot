# Changelog

All notable changes to the ConvoAI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-18

### Added - MCP Integration (Major Feature Release)

#### Model Context Protocol Support
- **MCP Server Management UI**: User-friendly interface to register and manage MCP servers
  - Simple form with name, description, server URL, and active toggle
  - No manual authentication required - user tokens automatically passed
  - Edit, delete, and activate/deactivate servers
- **Timezone MCP Server**: Reference implementation providing timezone tools
  - `get_current_time` tool for any timezone worldwide
  - JSON-RPC 2.0 compliant implementation
  - Bearer token authentication support
- **OpenAI Function Calling Integration**: Seamless tool discovery and execution
  - Automatic tool discovery from registered MCP servers
  - Dynamic OpenAI function calling with MCP tools
  - Real-time tool execution and response handling
- **MCP Tools Service**: Backend service for managing MCP interactions
  - Tool discovery via `tools/list` method
  - Tool execution via `tools/call` method
  - User token propagation to MCP servers
- **Database Schema**: Added `mcp_servers` table
  - User-scoped server management
  - Server configuration storage
  - Active/inactive server status

#### Documentation
- **Comprehensive MCP Documentation**: Complete guides for using and creating MCP servers
  - `MCP_README.md`: Detailed implementation guide
  - `timezone-mcp-server/README.md`: Reference server documentation
  - Updated main `README.md` with MCP integration overview
  - Updated service READMEs with MCP features
- **Manual Setup Guide**: Detailed instructions for running on host machine
  - Step-by-step service setup for all components
  - Virtual environment creation and activation
  - Dependency installation
  - Admin user creation
  - Environment configuration
- **CHANGELOG.md**: Version history and change tracking (this file)
- **VERSION**: Updated to 2.0.0 for major MCP feature

### Changed

#### Frontend
- **MCPServerManager Component**: Simplified UI removing authentication fields
  - Removed auth_type dropdown (bearer/api_key/none)
  - Removed conditional API key input field
  - Backend automatically handles authentication via user OAuth tokens
- **Token Management**: Fixed token retrieval from localStorage
  - Changed from `localStorage.token` to `localStorage.user.token`
  - Added proper error handling for token extraction
- **MCP Server Service**: Enhanced API client for MCP operations
  - Fixed authentication header injection
  - Improved error handling for server registration

#### Backend
- **Chat Service Schemas**: Simplified MCP server models
  - Removed `auth_type` and `api_key` from `MCPServerBase`
  - Removed authentication fields from `MCPServerUpdate`
  - Backend sets `auth_type="none"` and `api_key=None` automatically
- **MCP Server CRUD**: Updated to handle automatic authentication
  - User OAuth token automatically passed to MCP servers
  - No manual token/key management required
- **API Routes**: Removed unnecessary auth verification
  - Simplified MCP server registration endpoint
  - Fixed 503 Service Unavailable error
  - Removed incorrect auth-service verification call

### Fixed

#### MCP Integration Issues
- **Token Passing Bug**: Fixed user_token being None in MCP tool calls
  - Root cause: Token stored in nested user object in localStorage
  - Solution: Updated token retrieval logic in mcpServerService.js
- **Server URL Issue**: Fixed MCP server connection failures
  - Root cause: Using `localhost` instead of Docker service name
  - Solution: Updated default URL to use `timezone-mcp-server:8003/mcp`
- **503 Error on Registration**: Fixed MCP server creation failure
  - Root cause: Unnecessary auth-service verification call
  - Solution: Removed redundant authentication check
- **Schema Validation Error**: Fixed AttributeError for api_key field
  - Root cause: CRUD function referencing removed schema fields
  - Solution: Updated create_mcp_server to set fields as None

#### Tool Calling
- **Tool Discovery**: Fixed "All connection attempts failed" errors
  - Resolved token passing issue
  - Corrected server URL from localhost to Docker service name
  - Enhanced error logging for debugging

### Security
- **Automatic Token Propagation**: User OAuth tokens securely passed to MCP servers
- **User-Scoped Resources**: Each user can only access their own MCP servers
- **No Credential Storage**: No need to store API keys or tokens in database
- **Bearer Token Authentication**: Standardized authentication for MCP servers

---

## [1.1.0] - 2025-11-10

### Added
- **Analytics Service**: Comprehensive metrics tracking and reporting
  - Real-time analytics dashboard
  - User activity tracking
  - Conversation and message metrics
  - Token usage monitoring
  - Admin-only API endpoints
- **Analytics Middleware**: Automatic tracking for chat service
  - Request/response timing
  - Error rate tracking
  - API usage logging
- **Integrated Analytics Panel**: Frontend side panel showing metrics
  - Total users, conversations, messages
  - Token usage statistics
  - Recent user activity
  - Most active users leaderboard
  - Auto-refresh every 30 seconds
- **Cross-Service Communication**: Analytics service integration
  - Secure JWT-based communication
  - Activity logging from auth service
  - Real-time metrics from chat service

### Changed
- **Database Structure**: Added analytics database
  - `user_activity` table
  - `conversation_metrics` table
  - `message_metrics` table
  - `api_usage` table
  - `daily_stats` table
- **Service Architecture**: Expanded to 4-service microservices
  - Added analytics-service (Port 8002)
  - Updated docker-compose.yml
  - Added service discovery

### Fixed
- **CORS Configuration**: Added analytics service to allowed origins
- **Admin Role Validation**: Improved role-based access control
- **Database Paths**: Absolute path resolution for all databases

---

## [1.0.0] - 2025-10-15

### Added - Initial Release

#### Core Features
- **React Frontend**: Modern chat interface
  - User authentication (login/register)
  - Real-time messaging
  - Conversation management
  - Responsive design with gradient themes
- **OAuth 2.0 Authentication**: Secure user management
  - JWT token-based authentication
  - Role-based access control (RBAC)
  - User and role management APIs
  - Password hashing with bcrypt
- **ChatBot Service**: AI-powered conversations
  - OpenAI GPT integration
  - Conversation and message persistence
  - WebSocket real-time communication
  - User-scoped resource access
- **WebSocket Support**: Real-time bidirectional communication
  - Instant message delivery
  - Connection state management
  - Automatic reconnection
- **Hash-Based IDs**: Secure resource identifiers
  - User IDs (16 characters)
  - Conversation IDs (12 characters)
  - Message IDs (10 characters)

#### Infrastructure
- **Docker Support**: Complete containerization
  - Multi-service docker-compose configuration
  - Development and production Dockerfiles
  - Volume management for databases
  - Network isolation
- **Database Management**: SQLite databases for each service
  - Auth service: User and role management
  - Chat service: Conversations and messages
  - Automatic database initialization
- **Testing Suite**: Comprehensive end-to-end tests
  - Authentication flow tests
  - Chat API tests
  - WebSocket connection tests
  - Integration tests
  - 50+ test cases

#### Documentation
- **README.md**: Complete project documentation
- **Service READMEs**: Individual service documentation
- **Quick Start Guides**: Docker and local development
- **API Documentation**: Interactive Swagger/OpenAPI docs
- **Testing Documentation**: Test suite overview

### Security
- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: Bcrypt password security
- **CORS Configuration**: Controlled cross-origin access
- **User Isolation**: Strict ownership validation
- **Role-Based Access**: Admin, User, Manager roles

### Developer Experience
- **Hot Reload**: Development mode with auto-reload
- **Interactive API Docs**: Swagger UI for all services
- **Script Automation**: Platform-specific setup scripts
  - Windows batch scripts
  - Linux/Mac shell scripts
- **Environment Templates**: `.env.example` files
- **Logging**: Comprehensive logging across services

---

## Version History

- **2.0.0** (2025-11-18): MCP Integration - Major feature release with Model Context Protocol support
- **1.1.0** (2025-11-10): Analytics Service - Added comprehensive metrics and tracking
- **1.0.0** (2025-10-15): Initial Release - Core chat platform with OAuth 2.0

---

## Upgrade Notes

### Upgrading to 2.0.0 from 1.x.x

**Database Changes:**
- New table: `mcp_servers` (automatically created on first run)
- No migration required - new table is additive

**API Changes:**
- New endpoints: `/mcp-servers/` for MCP server management
- No breaking changes to existing endpoints

**Frontend Changes:**
- New component: `MCPServerManager` for managing MCP servers
- New button in chat interface to access MCP management
- No breaking changes to existing features

**Environment Variables:**
- No new required environment variables
- Optional: Add MCP server URLs for pre-registration

**Docker:**
- New service: `timezone-mcp-server` (Port 8003)
- Run `docker-compose up --build` to add new service
- No configuration changes required

**Local Development:**
- New service to run: `timezone-mcp-server`
- Follow manual setup guide for additional service
- Update scripts will handle new service automatically

---

## Contributors

- Development Team
- Community Contributors

## Support

For issues, questions, or contributions:
- GitHub Issues: Report bugs and request features
- Documentation: Check `/docs` directory for guides
- API Docs: Access `/docs` endpoint on each service
