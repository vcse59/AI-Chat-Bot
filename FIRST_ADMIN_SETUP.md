# 🚀 Quick Start - Create Your First Admin

**Issue**: When accessing http://localhost:3000/register-admin, you get redirected to login.

**Reason**: The `/register-admin` page requires you to be logged in as an admin user first.

---

## ✅ Solution: Bootstrap Your First Admin (One-Time Setup)

You need to create your first admin account before you can use the UI to create more admins.

### Option 1: Automated Script (Recommended)

Run the bootstrap script:

**Windows:**
```bash
bootstrap-admin.bat
```

**Linux/Mac:**
```bash
chmod +x bootstrap-admin.sh
./bootstrap-admin.sh
```

This will:
1. ✅ Create a user via API
2. ✅ Add admin role to database
3. ✅ Verify admin permissions
4. ✅ Show you the credentials

### Option 2: Manual Steps

1. **Register a user:**
   - Go to http://localhost:3000/register
   - Username: `admin`
   - Password: `admin123`
   - Click "Create Account"

2. **Add admin role to database:**
   ```bash
   docker exec -it auth-server sqlite3 /app/data/app.db "INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username='admin' AND r.name='admin';"
   ```

3. **Verify:**
   ```bash
   docker exec -it auth-server sqlite3 /app/data/app.db "SELECT u.username, r.name FROM users u JOIN user_roles ur ON u.id = ur.user_id JOIN roles r ON ur.role_id = r.id WHERE u.username='admin';"
   ```

---

## 🎯 After Bootstrap

1. **Login** at http://localhost:3000/login
   - Username: `admin`
   - Password: `admin123`

2. **Verify admin access** - You should see:
   - ✅ "📊 Analytics" button in header
   - ✅ "👤 Create Admin" button in header

3. **Now you can:**
   - Click "👤 Create Admin" to create more admin accounts via UI
   - Access http://localhost:3000/register-admin (will work now!)
   - View analytics at http://localhost:3000/analytics

---

## 📚 Full Documentation

- **`ADMIN_QUICK_START.md`** - Quick reference for all admin creation methods
- **`HOW_TO_CREATE_ADMIN.md`** - Comprehensive guide with troubleshooting
- **`ANALYTICS_DASHBOARD_COMPLETE.md`** - Analytics dashboard documentation

---

## 🔧 Troubleshooting

**Q: Still redirected to /login?**
- A: Make sure you logged in successfully and see the admin buttons in the header

**Q: No admin buttons after login?**
- A: Check localStorage: `JSON.parse(localStorage.getItem('user')).roles`
- Should contain: `["admin", "user"]`

**Q: Database command fails?**
- A: Make sure containers are running: `docker-compose ps`
- Auth-server should show "Up (healthy)"

---

**Need Help?** Check logs: `docker logs auth-server --tail 50`
