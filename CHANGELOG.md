# Changelog

All notable changes to the Open ChatBot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-11-16

### Added - Analytics Integration & Side Panel
- **Analytics Service (Port 8002)**: Complete admin-only analytics and metrics tracking service
  - User activity tracking (login, logout, conversations, messages)
  - API usage monitoring with response times and error rates
  - Conversation metrics (message count, token usage, avg response time)
  - Message metrics with token counting
  - Daily aggregated statistics
  - Admin-protected dashboard API endpoints
  - Public tracking endpoints for service-to-service communication
- **Analytics Middleware**: Automatic API usage tracking for all chatbot service requests
  - Fire-and-forget async tracking (non-blocking)
  - Request timing and status code logging
  - User identification from JWT tokens
- **Analytics Side Panel in Chat UI**: Real-time metrics display alongside conversations
  - Toggleable analytics panel (350px width)
  - Key metrics cards: Total Users, Active Users Today, Total Conversations, Total Messages, Total Tokens, Avg Response Time
  - Recent user activity list with timestamps and icons
  - Most active users leaderboard
  - Auto-refresh every 30 seconds
  - Manual refresh button
  - Responsive design with mobile overlay support
  - Active state indicator on Analytics button
- **Token Tracking**: Complete OpenAI token usage monitoring
  - Token count captured for every message
  - Aggregated at conversation level
  - Total tokens displayed in analytics summary
- **User Filtering**: Analytics endpoint to list users with activity filter
  - GET `/api/v1/analytics/users/list`
  - Query parameter: `active_only` (boolean)
  - Returns user_id, username, activity_count, last_activity, is_active_today
- **Service Integration**: Tracking integrated into auth and chatbot services
  - Login/logout tracking in auth service
  - Conversation creation/deletion tracking
  - Message creation tracking with tokens
  - Automatic user activity logging

### Changed
- **ChatPage Component**: Refactored to include analytics panel
  - Added `showAnalytics` state for panel toggle
  - Integrated analytics data loading
  - Added auto-refresh interval (30 seconds)
  - Enhanced header with active analytics button state
- **Analytics Summary**: Enhanced to include token counting
  - Added `total_tokens` field to AnalyticsSummary schema
  - Improved user counting from multiple tables
  - Uses max of users from UserActivity and ConversationMetrics
- **Database Schema**: Analytics database models for comprehensive tracking
  - UserActivity: user activities with timestamps
  - ConversationMetrics: per-conversation stats
  - MessageMetrics: per-message details with tokens
  - APIUsage: API call tracking
  - DailyStats: aggregated daily metrics
- **Frontend Services**: Added `analyticsService.js` for API client
  - Methods for summary, activities, top users, user list
  - Proper error handling and authentication

### Fixed
- **SQLAlchemy Type Checking**: Resolved Pylance errors in analytics router
  - Added `# type: ignore` comments for ORM operations
  - Used proper SQLAlchemy `.update()` method
  - Fixed column expression comparisons
- **Analytics Router**: Fixed missing `func` import from SQLAlchemy
  - Added `from sqlalchemy import func`
  - Enabled aggregation queries (count, sum, max)
- **Docker Build Caching**: Resolved file update issues
  - Used manual `docker cp` for critical updates
  - Verified file deployment in containers
  - Proper rebuild procedures documented

### Security
- **Admin-Only Analytics**: All analytics viewing endpoints protected by `require_admin` dependency
- **Public Tracking Endpoints**: Separate endpoints for service-to-service communication (no user auth)
  - Only accessible within Docker network
  - Not exposed to public internet
- **JWT Validation**: Consistent token validation across all services

## [2.5.0] - 2025-11-15

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
