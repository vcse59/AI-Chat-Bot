# 🚀 Startup Guide - Automatic Admin Setup

## Overview

The ConvoAI platform now features **automatic admin user creation** on first startup! No more manual database commands or scripts needed.

## ✨ What's Automatic?

When you start the services for the first time, the auth-server automatically:

1. ✅ Creates database tables
2. ✅ Initializes default roles (admin, user, manager)
3. ✅ Creates an admin user with credentials from environment variables
4. ✅ Assigns both 'admin' and 'user' roles to the admin account
5. ✅ Makes the admin immediately ready to use

## 🎯 Quick Start (3 Steps)

### 1. Configure Admin Credentials (Optional)

Edit `.env` file or create one from `.env.example`:

```env
# Change these before first run for security!
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

# Also set these required values
AUTH_SECRET_KEY=your-secure-secret-key-at-least-32-characters-long
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Security Tip**: Change `ADMIN_PASSWORD` before first run!

### 2. Start All Services

```bash
docker-compose up -d --build
```

### 3. Verify Admin Creation

Check the logs to confirm admin user was created:

```bash
docker logs auth-server --tail 20
```

You should see:
```
Creating role: admin
Creating role: user
Creating role: manager
Creating admin user: admin
Assigned 'admin' role to admin
Assigned 'user' role to admin
✅ Admin user 'admin' created successfully!
   Username: admin
   Password: admin123
   Email: admin@example.com
```

## 🎉 You're Ready!

**Login to the app:**
1. Go to http://localhost:3000/login
2. Username: `admin` (or your custom ADMIN_USERNAME)
3. Password: `admin123` (or your custom ADMIN_PASSWORD)

**You'll have immediate access to:**
- 📊 **Analytics Dashboard** - Click "📊 Analytics" button in header
- 👤 **Create Admin** - Click "👤 Create Admin" to add more admins
- 💬 **Full Chat Features** - All user features plus admin capabilities

## 🔄 Subsequent Startups

On subsequent startups, the system detects that the admin user already exists and skips creation:

```bash
docker-compose up -d
# OR
docker-compose restart
```

You'll see in logs:
```
Admin user 'admin' already exists
```

This prevents duplicate admin creation and ensures idempotent startup.

## 🔧 Customization

### Change Admin Credentials

Set these environment variables in `.env`:

```env
ADMIN_USERNAME=myadmin
ADMIN_PASSWORD=MySecureP@ssw0rd!
ADMIN_EMAIL=admin@mycompany.com
```

### Multiple Admin Users

After the first admin is created, you can:

1. **Via UI**: 
   - Login as admin
   - Click "👤 Create Admin" button
   - Fill in new admin details

2. **Via API**:
   ```bash
   curl -X POST http://localhost:8001/api/v1/users/ \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "secondadmin",
       "email": "admin2@example.com",
       "password": "SecurePass123",
       "roles": ["admin", "user"]
     }'
   ```

## 📝 Technical Details

### How It Works

The admin creation logic is in `auth-service/auth_server/main.py`:

```python
def init_admin_user():
    """Initialize default admin user if it doesn't exist."""
    # Gets credentials from env vars
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Checks if admin exists
    existing_admin = db.query(User).filter_by(username=admin_username).first()
    if existing_admin:
        return  # Skip if exists
    
    # Creates admin with both admin and user roles
    # ... (creation logic)
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_USERNAME` | `admin` | Admin account username |
| `ADMIN_PASSWORD` | `admin123` | Admin account password |
| `ADMIN_EMAIL` | `admin@example.com` | Admin email address |

### Execution Order

1. Database tables created
2. Default roles initialized
3. Admin user checked/created
4. FastAPI app started
5. Services become healthy

## 🆘 Troubleshooting

### Admin Not Created

**Check logs:**
```bash
docker logs auth-server
```

**Common issues:**
- Database volume persists old data: `docker compose down -v` to clean
- Container not healthy: Check `docker compose ps`
- Permission errors: Check volume mounts

### Reset Everything

To start completely fresh:

```bash
# Stop and remove all containers and volumes
docker compose down -v

# Rebuild and start
docker compose up -d --build

# Check logs
docker logs auth-server --tail 30
```

### Can't Login

1. Verify admin was created in logs
2. Check you're using correct credentials from .env
3. Try clearing browser cache
4. Check auth-server is healthy: `docker compose ps`

## 🎓 Learning More

- **Admin Features**: See `ANALYTICS_DASHBOARD_COMPLETE.md`
- **User Management**: See `HOW_TO_CREATE_ADMIN.md`
- **Full Setup**: See main `README.md`

## ✅ Summary

**Before (Manual Setup):**
```bash
# Register user
# Run SQL command
# Verify in database
# Finally login
```

**Now (Automatic):**
```bash
docker-compose up -d
# Login with admin/admin123
# Done! 🎉
```

---

**The admin setup is now completely automated - just start the services and login!**
