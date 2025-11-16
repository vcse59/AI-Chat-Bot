# Admin Account Creation - Quick Reference

## 🎯 Three Ways to Create Admin Accounts

### 1️⃣ First Admin (Bootstrap) - One-Time Setup

**⚠️ IMPORTANT**: You need to do this BEFORE accessing `/register-admin` URL!

**Method A - Automated Script (Easiest):**
```bash
# Windows:
bootstrap-admin.bat

# Linux/Mac:
chmod +x bootstrap-admin.sh
./bootstrap-admin.sh
```

**Method B - Manual Steps:**
```bash
# 1. Register at http://localhost:3000/register
#    Username: admin
#    Password: admin123

# 2. Access database
docker exec -it auth-server sqlite3 /app/data/app.db

# 3. Add admin role (one command)
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id FROM users u, roles r 
WHERE u.username='admin' AND r.name='admin';

# 4. Verify
SELECT u.username, r.name FROM users u 
JOIN user_roles ur ON u.id = ur.user_id 
JOIN roles r ON ur.role_id = r.id 
WHERE u.username = 'admin';

# 5. Exit
.quit

# 6. Login at http://localhost:3000/login
```

### 2️⃣ From UI (Recommended) - For Existing Admins

**⚠️ Prerequisites**: You must be logged in as an admin user first!

**Steps:**
1. Login as admin at http://localhost:3000/login
2. Click "👤 Create Admin" button in header
3. Fill in the form:
   - Username (required)
   - Email (required)
   - Full Name (optional)
   - Password (min 6 chars)
   - Confirm Password
4. Click "🔐 Create Admin Account"
5. Success! New admin can login immediately

**Direct URL:** http://localhost:3000/register-admin (requires admin login)

**Note:** If you try to access `/register-admin` without being logged in as admin, you'll be redirected to `/login`.

### 3️⃣ Via API - For Automation

**Request:**
```bash
# Get token first
curl -X POST http://localhost:8001/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Create admin (replace TOKEN with actual token)
curl -X POST http://localhost:8001/api/auth/register-admin \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"username":"newadmin","email":"admin@example.com","password":"admin123"}'
```

---

## ✅ What Admin Users Can Do

- ✅ Access Analytics Dashboard (📊 button in header)
- ✅ Create more admin accounts (👤 button in header)
- ✅ View all system metrics and statistics
- ✅ Track user activities
- ✅ Access all admin API endpoints
- ✅ Full chat functionality

## ❌ What Regular Users Cannot Do

- ❌ No Analytics button visible
- ❌ No Create Admin button visible
- ❌ Cannot access /analytics (Access Denied page)
- ❌ Cannot access /register-admin (Access Denied page)
- ❌ Cannot call admin API endpoints (403 Forbidden)

---

## 🚀 Quick Test

**After creating your first admin:**

1. Login at http://localhost:3000
2. Look for these buttons in header: `📊 Analytics | 👤 Create Admin`
3. If you see them → **Success!** ✅
4. If not → Check roles in localStorage: `JSON.parse(localStorage.getItem('user')).roles`

---

## 📱 UI Features

**Admin Registration Page:**
- ✅ Form validation (password match, min length)
- ✅ Success messages (green)
- ✅ Error messages (red)
- ✅ Auto-redirect after success
- ✅ Cancel button to go back
- ✅ Clean, modern design

**Security:**
- 🔐 Admin-only access (JWT validation)
- 🔐 Route protection on frontend
- 🔐 API endpoint protection on backend
- 🔐 Passwords hashed with bcrypt
- 🔐 Token-based authentication

---

## 🔗 Useful URLs

| Page | URL | Access |
|------|-----|--------|
| Login | http://localhost:3000/login | Public |
| Register (User) | http://localhost:3000/register | Public |
| Register (Admin) | http://localhost:3000/register-admin | **Admin Only** |
| Analytics | http://localhost:3000/analytics | **Admin Only** |
| Chat | http://localhost:3000/chat | Authenticated |
| API Docs | http://localhost:8001/docs | Public |

---

## 🐛 Troubleshooting

**"Create Admin" button not showing?**
- Check: `JSON.parse(localStorage.getItem('user')).roles`
- Should contain: `["admin", "user"]`
- Fix: Update database or logout/login again

**403 Forbidden when creating admin?**
- Logout and login again to refresh token
- Verify JWT includes admin role
- Check .env AUTH_SECRET_KEY matches

**Access Denied page appears?**
- You're not logged in as admin
- Bootstrap your first admin (see Method 1)

---

## 📚 Full Documentation

See `HOW_TO_CREATE_ADMIN.md` for detailed guide with:
- Complete bootstrap instructions
- Database schema details
- API endpoint documentation
- Testing procedures
- Error handling
- Security considerations

---

**Need Help?** Check the full documentation or container logs:
```bash
docker logs auth-server --tail 50
docker logs chat-frontend --tail 50
```
