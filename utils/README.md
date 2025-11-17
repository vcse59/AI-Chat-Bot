# ConvoAI Utility Scripts

This directory contains utility scripts and standalone test scripts for the ConvoAI platform.

## 📁 Script Categories

### User Management Scripts
- **`check_roles.py`** - Check user roles and permissions in the authentication database
- **`list_users.py`** - List all users with their details from the auth database

### Database Migration Scripts
- **`migrate_to_single_db.py`** - Database migration utility for consolidating databases

### Standalone Test Scripts
- **`test_analytics_flow.py`** - Test the analytics service endpoints and data flow
- **`test_auth_flow.py`** - Test authentication flow (registration, login, token validation)
- **`test_conversation.py`** - Test conversation creation and message handling

## 🚀 Usage

### User Management

**Check User Roles:**
```bash
# From project root
cd utils
python check_roles.py
```

**List All Users:**
```bash
cd utils
python list_users.py
```

### Database Migration

**Migrate to Single Database:**
```bash
cd utils
python migrate_to_single_db.py
```

### Running Standalone Tests

**Test Authentication Flow:**
```bash
cd utils
python test_auth_flow.py
```

**Test Conversation Flow:**
```bash
cd utils
python test_conversation.py
```

**Test Analytics Flow:**
```bash
cd utils
python test_analytics_flow.py
```

## 📝 Notes

- **Database Scripts**: These scripts access the SQLite databases directly. Ensure services are stopped before running database migration scripts.
- **Test Scripts**: These are standalone integration test scripts. For comprehensive testing, use the test suite in the `tests/` directory.
- **Dependencies**: Most scripts require the same dependencies as the main services. Ensure you have the necessary packages installed.

## 🔗 Related Documentation

- [Main README](../README.md) - Project overview
- [Testing Documentation](../tests/README.md) - Comprehensive test suite
- [Scripts Documentation](../scripts/README.md) - Service management scripts
- [Documentation Hub](../docs/README.md) - All documentation

## ⚠️ Important

- Always backup your databases before running migration scripts
- Run user management scripts when services are running (they query live databases)
- Test scripts can be run independently but ensure services are running
- For production environments, use proper backup and migration procedures

## 🛠️ Development

These scripts are primarily for:
- Development and debugging
- Database inspection and management
- Quick integration testing
- Data migration between versions

For production deployments, refer to the main deployment documentation.
