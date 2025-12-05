# Release v3.0.0 - Theme Toggle, Cross-Platform Support & Documentation Enhancement

**Release Date:** December 5, 2025

## 🎉 Major Release Highlights

ConvoAI v3.0.0 is a **major feature release** introducing comprehensive theme customization, enhanced cross-platform support, standalone service deployment capabilities, and improved documentation across all components.

---

## ✨ Major New Features

### 🎨 Theme Toggle Support

#### User-Customizable Themes
- **Dark/Light Mode Toggle**: All authenticated pages now support theme switching
- **User Preference Persistence**: Theme preference stored in user profile database
- **Real-time Theme Switching**: Instant visual feedback with smooth transitions
- **Theme-Agnostic Authentication**: Login and Register pages use a consistent, standalone design with ConvoAI branding

#### Themed Pages
- **ChatPage**: Full dark/light theme support with CSS variables
- **AnalyticsDashboard**: Theme-aware metrics and charts
- **UserManagement**: Admin panel with theme support
- **WorkflowTemplates**: LangChain workflow interface with theming
- **RegisterAdmin**: Admin registration with theme toggle

#### CSS Variable System
- **Centralized Theme Variables**: All colors defined in `theme.css`
- **Dynamic Color Switching**: Background, text, border, and shadow colors
- **Component-Level Styling**: MetricsCard, WorkflowTemplate components updated
- **Consistent Design Language**: Uniform look across all components

### 📦 Standalone Service Deployment

#### Independent Service Operation
- **Per-Service .env.example Files**: Comprehensive configuration templates for all services
- **Dockerfile-Based Deployment**: Each service can run independently with Docker
- **Local Development Support**: Full instructions for running without Docker

#### Services with Standalone Support
| Service | Port | .env.example | README Updated |
|---------|------|--------------|----------------|
| auth-service | 8001 | ✅ | ✅ |
| chat-service | 8000 | ✅ | ✅ |
| analytics-service | 8002 | ✅ | ✅ |
| langchain-service | 8004 | ✅ | ✅ |
| timezone-mcp-server | 8003 | ✅ | ✅ |
| chat-frontend | 3000 | ✅ | ✅ |

### 🖥️ Cross-Platform Documentation

#### Multi-Platform Instructions
- **Windows (PowerShell)**: Full PowerShell command support
- **Windows (Command Prompt)**: CMD-compatible instructions
- **Linux**: Bash commands and scripts
- **macOS**: Unix-compatible commands

#### Platform-Specific Commands
- Docker volume mounting (`$(pwd)` vs `${PWD}` vs `%cd%`)
- Directory creation (`mkdir -p` vs `New-Item` vs `mkdir`)
- File copying (`cp` vs `Copy-Item` vs `copy`)
- Environment activation (`source` vs `Scripts\activate`)

---

## 🔧 Technical Improvements

### Pydantic Model Fixes
- **Protected Namespace Warning**: Fixed `model_used` field conflicts in analytics-service
- **ConfigDict Updates**: Added `protected_namespaces=()` to affected schemas
- **Clean Startup**: No more Pydantic warnings in service logs

#### Fixed Schemas
- `MessageMetricsSchema` - analytics/schemas/analytics.py
- `MessageDetailedMetrics` - analytics/schemas/analytics.py
- `MessageTrackingRequest` - analytics/routers/analytics.py

### Database Enhancements
- **theme_preference Column**: Added to users table for theme persistence
- **User Deletion Sync**: Theme preference included in user profile operations
- **Migration Support**: Automatic column creation on startup

### Frontend Architecture
- **ThemeContext Provider**: React context for global theme state
- **useTheme Hook**: Easy access to theme state and toggle function
- **CSS Variable Integration**: Dynamic styling without component re-renders

---

## 📚 Documentation Updates

### README Files Enhanced
All service READMEs now include:
1. **Quick Start Section** with three deployment options:
   - Docker Compose (recommended)
   - Standalone Docker Container
   - Local Development
2. **Cross-Platform Commands** for:
   - Windows PowerShell
   - Windows Command Prompt
   - Linux/macOS

### Environment Configuration
- **Comprehensive .env.example Files**: Full documentation of all environment variables
- **Grouped Configuration Sections**: Server, Database, Auth, CORS, Logging
- **Usage Comments**: Inline documentation for each variable

### Updated Documentation Files
- `auth-service/README.md`
- `chat-service/README.md`
- `analytics-service/README.md`
- `langchain-service/README.md`
- `timezone-mcp-server/README.md`
- `chat-frontend/README.md`
- `CHANGELOG.md`
- `docs/VERSIONING.md`
- `RELEASES_SUMMARY.md`

---

## 🐛 Bug Fixes

### Theme System
- Fixed theme persistence across page navigation
- Fixed theme toggle button visibility on all pages
- Fixed CSS variable inheritance issues

### Service Startup
- Resolved Pydantic `protected_namespaces` warnings
- Fixed duplicate import statements in analytics router
- Cleaned up service startup logs

### Documentation
- Fixed inconsistent cross-platform instructions
- Added missing Windows CMD commands
- Corrected volume mount syntax for different shells

---

## 🔒 Security Updates

### Theme Preference Storage
- Theme stored server-side in user profile
- No client-side storage of theme (using database)
- Theme synced on login

### Service Isolation
- Each service can run independently
- Proper environment variable isolation
- Secure default configurations in .env.example files

---

## 📊 Service Status

### All Services Healthy
| Service | Status | Health Endpoint |
|---------|--------|-----------------|
| auth-server | ✅ Running | /health |
| openai-chatbot-api | ✅ Running | /health |
| analytics-service | ✅ Running | /health |
| langchain-service | ✅ Running | /health |
| timezone-mcp-server | ✅ Running | /health |
| chat-frontend | ✅ Running | nginx |

---

## 🚀 Upgrade Guide

### From v2.0.0 to v3.0.0

1. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

2. **Update Environment Files**
   ```bash
   # Copy new .env.example files for each service
   cp auth-service/.env.example auth-service/.env
   cp chat-service/.env.example chat-service/.env
   # ... repeat for other services
   ```

3. **Rebuild Docker Images**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

4. **Database Migration**
   - `theme_preference` column added automatically on auth-server startup
   - No manual migration required

### Breaking Changes
- None - v3.0.0 is backward compatible with v2.0.0

---

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.

---

## 🙏 Contributors

Thank you to all contributors who made this release possible!

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/vcse59/ConvoAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vcse59/ConvoAI/discussions)
