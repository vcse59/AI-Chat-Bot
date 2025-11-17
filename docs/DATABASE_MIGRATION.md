# Database Consolidation Guide

## Overview

The application has been migrated from **3 separate databases** to **1 unified database**:

### Before (3 Databases):
- `auth_data` volume → `auth.db` (users, roles, user_roles)
- `chatbot_data` volume → `openai_chatbot.db` (conversations, messages)  
- `analytics_data` volume → `analytics.db` (analytics tables)

### After (1 Database):
- `shared_data` volume → `chatbot.db` (all tables in one database)

## Changes Made

### 1. Docker Compose Configuration
- ✅ Created single `shared_data` volume
- ✅ Removed `auth_data`, `chatbot_data`, `analytics_data` volumes
- ✅ All services now mount `shared_data:/app/data`
- ✅ All services use `DATABASE_URL=sqlite:///./data/chatbot.db`

### 2. Service Database Configurations
- ✅ `auth-service` updated to read from environment `DATABASE_URL`
- ✅ `openai_web_service` updated to read from environment `DATABASE_URL`
- ✅ `analytics-service` updated to read from environment `DATABASE_URL`

### 3. Unified Schema
All tables now exist in a single `chatbot.db`:

**Auth Tables:**
- `users` - User accounts
- `roles` - User roles (admin, user, etc.)
- `user_roles` - User-to-role mapping

**Chatbot Tables:**
- `conversations` - Chat conversations
- `messages` - Chat messages

**Analytics Tables:**
- `user_activity` - User activity tracking
- `conversation_metrics` - Conversation statistics
- `message_metrics` - Message statistics
- `api_usage` - API usage tracking
- `daily_stats` - Daily aggregated statistics

## Migration Steps

### Option 1: Fresh Start (Recommended for Development)

If you don't need to preserve existing data:

```bash
# Stop all containers
docker compose down

# Remove old volumes
docker volume rm open-chatbot_auth_data open-chatbot_chatbot_data open-chatbot_analytics_data

# Start with new unified database
docker compose up -d --build
```

The services will automatically create the new unified database with all required tables.

### Option 2: Migrate Existing Data

If you need to preserve existing data:

#### Step 1: Export existing data from containers

```bash
# Create backup directory
mkdir -p ./backups

# Export databases from containers
docker cp auth-server:/app/data/auth.db ./backups/auth.db
docker cp openai-chatbot-api:/app/data/openai_chatbot.db ./backups/openai_chatbot.db
docker cp analytics-service:/app/analytics.db ./backups/analytics.db
```

#### Step 2: Run migration script

```bash
# Install Python (if not already installed)
# Then run the migration script
python migrate_to_single_db.py \
  --auth-db ./backups/auth.db \
  --chatbot-db ./backups/openai_chatbot.db \
  --analytics-db ./backups/analytics.db \
  --target-db ./data/chatbot.db
```

#### Step 3: Deploy unified database

```bash
# Stop containers
docker compose down

# Remove old volumes
docker volume rm open-chatbot_auth_data open-chatbot_chatbot_data open-chatbot_analytics_data

# Create shared volume and copy unified database
docker volume create open-chatbot_shared_data
docker run --rm -v open-chatbot_shared_data:/data -v ${PWD}/data:/backup alpine cp /backup/chatbot.db /data/chatbot.db

# Start services
docker compose up -d --build
```

### Option 3: In-Container Migration (Advanced)

```bash
# Copy migration script to auth-server container
docker cp migrate_to_single_db.py auth-server:/app/

# Run migration inside container
docker exec -it auth-server python /app/migrate_to_single_db.py \
  --auth-db /app/data/auth.db \
  --chatbot-db /app/data/openai_chatbot.db \
  --analytics-db /app/analytics.db \
  --target-db /app/data/chatbot.db

# Restart services
docker compose restart
```

## Verification

After migration, verify the unified database:

```bash
# Connect to any service and check the database
docker exec -it auth-server sqlite3 /app/data/chatbot.db

# In SQLite shell:
.tables                    # List all tables
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM user_activity;
.quit
```

## Benefits of Single Database

1. **Simplified Architecture**: One database to manage instead of three
2. **Easier Backups**: Single backup file contains all data
3. **Better Data Integrity**: Foreign key relationships work across all tables
4. **Reduced Complexity**: Fewer volumes and configuration
5. **Consistent Transactions**: All data changes in one ACID-compliant database

## Rollback Instructions

If you need to rollback to the old 3-database setup:

1. Restore `docker-compose.yml` from git history
2. Restore the three service database configuration files
3. Copy your backup databases back to their original locations
4. Run `docker compose up -d --build`

## Troubleshooting

### Database not found error
- Ensure the `shared_data` volume exists: `docker volume ls`
- Check container logs: `docker logs auth-server`
- Verify DATABASE_URL environment variable is set correctly

### Migration script errors
- Ensure all source databases exist in specified paths
- Check file permissions
- Review error messages in the migration output

### Foreign key constraint errors
- The unified database maintains all foreign key relationships
- If you see constraint errors, check data consistency in source databases

## Support

For issues or questions about the migration, please:
1. Check container logs: `docker compose logs`
2. Verify database connectivity: `docker exec -it auth-server ls -la /app/data/`
3. Test database access: `docker exec -it auth-server sqlite3 /app/data/chatbot.db ".tables"`
