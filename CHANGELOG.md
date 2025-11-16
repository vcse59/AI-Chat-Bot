# Changelog

All notable changes to the Open ChatBot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Full OAuth 2.0 authentication and authorization system
- JWT token-based authentication with role-based access control (RBAC)
- Real-time WebSocket communication for chat messages
- OpenAI GPT integration for AI-powered conversations
- User auto-provisioning in chat database when authenticated
- Hash-based IDs for users and conversations (security)
- Conversation-specific WebSocket endpoint (`/ws/{conversation_id}`)
- User profile support with `full_name` field
- Comprehensive authentication flow testing
- Docker containerization for all services
- Health check endpoints for all services
- CORS configuration for frontend-backend communication
- WebSocket reconnection logic with configurable retry attempts
- **DELETE endpoint for conversations**: `DELETE /api/v1/users/{user_id}/conversations/{conversation_id}`

### Changed
- **OpenAI API Migration**: Updated from v0.x to v1.x+ API
  - Changed from `openai.ChatCompletion.acreate()` to `client.chat.completions.create()`
  - Updated error handling: `openai.error.*` → `openai.*Error`
  - Now using `AsyncOpenAI` client for async operations
- **Authentication**: SECRET_KEY now loaded from environment variables
- **WebSocket Protocol**: Updated message format to structured JSON
  - Old format: `{message: "...", conversation_id: "..."}`
  - New format: `{type: "send_message", data: {conversation_id: "...", content: "..."}}`
- **Permission Checks**: Fixed user ID comparison in all endpoints
  - Now properly compares username from JWT with database user records
  - Added user lookup by username before permission validation
- **Frontend Message Handling**: Enhanced to process both user and AI responses
  - Implements optimistic UI updates with confirmation
  - Proper handling of WebSocket response messages
- **WebSocket Reconnection**: Improved reconnection logic
  - Added `preventReconnect` parameter to `disconnect()` method
  - Reset reconnection counter after max attempts for future connections
  - Proper handling of conversation switching without blocking new connections
- **Type Hints**: Updated parameter types from int to str for hash-based IDs
  - Changed user_id parameters from `int` to `str`
  - Changed conversation_id parameters from `int` to `str`
  - Fixed return type covariance issues

### Fixed
- User registration now accepts and stores `full_name` field
- JWT token signature verification across auth and chat services
- Database schema migration for `full_name` column
- Role field handling in OpenAI service (string vs enum)
- WebSocket reconnection failures when switching between conversations
  - Fixed: "Failed to reconnect after maximum attempts" error
  - Proper cleanup prevents reconnection blocking on conversation changes
  - Reconnection counter now resets appropriately
- **Conversation deletion**: Added missing DELETE endpoint
  - Fixed: "Not Found" error when deleting conversations
  - Endpoint now properly validates user ownership before deletion
  - Supports both username and user ID in path parameter
- Permission validation in 9 endpoints:
  - POST `/conversations/{conversation_id}/messages/`
  - GET `/conversations/{conversation_id}/messages/`
  - POST `/users/{user_id}/conversations/`
  - GET `/users/{user_id}/conversations/`
  - POST `/users/{user_id}/conversations/{conversation_id}/reconnect`
  - GET `/users/{user_id}/conversations/{conversation_id}/validate`
  - GET `/users/{user_id}/conversations/recent`
  - POST `/users/{user_id}/conversations/{conversation_id}/end`
  - GET `/users/{user_id}/conversations/{conversation_id}/stats`
- Type-checking issues in `openai_service.py`
  - Updated all ID-related parameters to use `str` instead of `int`
  - Fixed return type mismatch using `Sequence` for covariance

### Security
- Hash-based IDs (16 chars for users, 12 for conversations, 10 for messages)
- JWT token validation with shared secret between services
- User-scoped resource access with ownership validation
- BCrypt password hashing with salt
- Environment-based secret key configuration

## [2.0.0] - 2025-11-15

### Added
- Complete microservices architecture with Docker Compose
- React frontend with modern UI and real-time chat
- FastAPI backend services (Auth + ChatBot)
- SQLite databases for persistence
- Comprehensive test suite with 50+ tests

### Changed
- Migrated from monolithic to microservices architecture
- Separated authentication and chat services
- Implemented OAuth 2.0 authentication flow

### Fixed
- Initial release - baseline functionality

## [1.0.0] - Initial Release

- Basic chat functionality
- Simple authentication
- Monolithic architecture

---

For upgrade instructions and breaking changes, see [README.md](README.md)
