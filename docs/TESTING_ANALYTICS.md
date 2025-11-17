# Testing the Analytics Dashboard

## Quick Test Checklist

### ✅ Pre-Test Verification
- [ ] All 4 containers running: `docker-compose ps`
- [ ] Frontend accessible: http://localhost:3000
- [ ] Auth service healthy: http://localhost:8001/docs
- [ ] Analytics service healthy: http://localhost:8002/docs

### 🔧 Setup Admin User (Choose One Method)

#### Method 1: Via Auth API (Easiest)
```bash
# 1. Register user
curl -X POST http://localhost:8001/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin123\"}"

# 2. Login to get token
curl -X POST http://localhost:8001/api/auth/token ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin&password=admin123"

# 3. You'll need to manually add admin role to database (see Method 2)
```

#### Method 2: Direct Database Update
```bash
# Access auth database
docker exec -it auth-server sqlite3 /app/data/app.db

# Check current users
SELECT id, username, email FROM users;

# If using user_roles table (check your schema)
# You'll need to insert admin role for the user
# This depends on your exact database schema

.quit
```

#### Method 3: Using Auth API Docs
1. Open http://localhost:8001/docs
2. Use `/api/auth/register` endpoint to create user
3. Check response for user details
4. Use database access to add admin role (temporary until admin promotion endpoint is created)

### 🧪 Test Cases

#### Test 1: Admin Login & Dashboard Access ✅
**Expected Result**: Admin user sees analytics button and can access dashboard

1. Open http://localhost:3000
2. Login with admin credentials
3. **Verify**: "📊 Analytics" button visible in header (between username and logout)
4. Click "📊 Analytics" button
5. **Verify**: Navigate to http://localhost:3000/analytics
6. **Verify**: Dashboard loads with:
   - 6 metric cards (Total Users, Active Users, Conversations, Messages, Tokens, Avg Response Time)
   - Recent Activities section (with pagination)
   - Top Users section (top 5 ranked)
7. **Verify**: All metrics show numbers or "N/A" if no data
8. Click "🔄 Refresh" button
9. **Verify**: Loading state appears briefly, then data reloads

**Success Indicators**:
- ✅ Analytics button visible
- ✅ Dashboard accessible
- ✅ Metrics display correctly
- ✅ No console errors
- ✅ API calls return 200 OK

**Failure Scenarios**:
- ❌ 403 error → User doesn't have admin role in JWT
- ❌ 401 error → Token expired or invalid
- ❌ Button not visible → Check localStorage for roles array
- ❌ Dashboard empty → Check analytics database for data

---

#### Test 2: Non-Admin User Access ❌
**Expected Result**: Regular user cannot see button or access dashboard

1. Logout from admin account (or use incognito window)
2. Register new user: http://localhost:3000/register
3. Login with regular user credentials
4. **Verify**: "📊 Analytics" button **NOT visible** in header
5. Manually navigate to http://localhost:3000/analytics
6. **Verify**: Access Denied page displays:
   ```
   🚫 Access Denied
   
   This page requires admin privileges.
   You need to be an admin to view analytics.
   
   [Go to Chat]
   ```
7. Click "Go to Chat" button
8. **Verify**: Redirects to http://localhost:3000/chat

**Success Indicators**:
- ✅ Analytics button hidden for non-admin
- ✅ Access Denied page shows for direct URL access
- ✅ "Go to Chat" button works
- ✅ No console errors about unauthorized access

**Failure Scenarios**:
- ❌ Button visible → isAdmin() not working correctly
- ❌ Dashboard accessible → AdminRoute not protecting route
- ❌ No Access Denied page → AdminRoute not rendering fallback

---

#### Test 3: Authentication Flow 🔐
**Expected Result**: Unauthenticated users redirected to login

1. Clear localStorage: `localStorage.clear()` in browser console
2. Navigate to http://localhost:3000/analytics
3. **Verify**: Redirect to http://localhost:3000/login
4. Login with admin credentials
5. **Verify**: Redirect to http://localhost:3000/analytics
6. **Verify**: Dashboard loads successfully

**Success Indicators**:
- ✅ Redirect to login page when not authenticated
- ✅ Return to dashboard after login
- ✅ Token stored in localStorage
- ✅ User data includes roles array

---

#### Test 4: JWT Token & Roles 🎫
**Expected Result**: Token properly decoded with roles array

1. Login as admin
2. Open browser DevTools → Console
3. Run: `JSON.parse(localStorage.getItem('user'))`
4. **Verify**: Output shows:
   ```javascript
   {
     token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     tokenType: "bearer",
     username: "admin",
     roles: ["admin", "user"],  // ← Must include "admin"
     sub: "123",
     exp: 1731739200
   }
   ```
5. Run: `JSON.parse(localStorage.getItem('user')).roles.includes('admin')`
6. **Verify**: Returns `true`

**Success Indicators**:
- ✅ User object contains roles array
- ✅ Admin role present in array
- ✅ Token not expired (exp > current time)
- ✅ Sub field contains user ID

**Failure Scenarios**:
- ❌ roles undefined → JWT not decoded correctly
- ❌ roles empty → Backend not including roles in token
- ❌ "admin" not in array → User not promoted to admin

---

#### Test 5: API Communication 📡
**Expected Result**: Dashboard makes successful API calls

1. Login as admin
2. Navigate to http://localhost:3000/analytics
3. Open DevTools → Network tab
4. **Verify**: API calls made to:
   - `GET http://localhost:8002/api/v1/analytics/summary`
   - `GET http://localhost:8002/api/v1/analytics/users/activities?skip=0&limit=10`
   - `GET http://localhost:8002/api/v1/analytics/users/top?limit=5`
5. Click on each request in Network tab
6. **Verify**: Request headers include:
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
7. **Verify**: Response status is `200 OK`
8. **Verify**: Response body contains analytics data

**Success Indicators**:
- ✅ All API calls return 200
- ✅ Authorization header present
- ✅ Response data matches dashboard display
- ✅ No CORS errors

**Failure Scenarios**:
- ❌ 403 error → Check admin role in JWT
- ❌ 401 error → Token expired or invalid
- ❌ 404 error → Analytics service not running
- ❌ CORS error → Check nginx.conf proxy settings

---

#### Test 6: Data Display & Updates 📊
**Expected Result**: Dashboard shows correct data and updates

1. **Generate Some Data First**:
   ```bash
   # Login/logout a few times to create activities
   # Send messages in chat to create conversation data
   ```

2. Login as admin → Open analytics dashboard
3. **Verify**: Metrics show non-zero values
4. Note down current "Total Messages" count
5. Go to chat page, send a few messages
6. Return to analytics, click "🔄 Refresh"
7. **Verify**: Message count increased
8. **Verify**: Recent activities show new entries
9. Scroll through activities
10. **Verify**: Activity icons match types:
    - 🔐 login
    - 🚪 logout
    - 📡 api_call
    - ✏️ message_sent
    - 📥 message_received
    - ⚙️ settings_change
    - 🔄 sync
    - ❓ other

**Success Indicators**:
- ✅ Metrics display accurate data
- ✅ Refresh updates values
- ✅ Activities list shows recent entries
- ✅ Timestamps are relative (X minutes ago)
- ✅ Top users ranked correctly

---

#### Test 7: Error Handling ⚠️
**Expected Result**: Graceful error handling for failures

1. **Test 7a: Service Down**
   ```bash
   docker stop analytics-service
   ```
   - Refresh dashboard
   - **Verify**: Error message displays: "Failed to load data"
   - **Verify**: No page crash, error boundary works
   ```bash
   docker start analytics-service
   ```

2. **Test 7b: Token Expiration**
   - In DevTools console:
     ```javascript
     const user = JSON.parse(localStorage.getItem('user'));
     user.exp = Math.floor(Date.now() / 1000) - 1;
     localStorage.setItem('user', JSON.stringify(user));
     ```
   - Refresh page
   - **Verify**: Redirect to login page

3. **Test 7c: Invalid Token**
   - In DevTools console:
     ```javascript
     const user = JSON.parse(localStorage.getItem('user'));
     user.token = 'invalid_token';
     localStorage.setItem('user', JSON.stringify(user));
     ```
   - Refresh dashboard
   - **Verify**: 401 error shown, redirect to login

**Success Indicators**:
- ✅ Error messages display clearly
- ✅ No console errors or crashes
- ✅ User redirected appropriately
- ✅ Recovery possible (login again)

---

### 🐛 Debugging Common Issues

#### Issue: "Admin button not visible"
**Diagnosis**:
```javascript
// In browser console:
const user = JSON.parse(localStorage.getItem('user'));
console.log('User:', user);
console.log('Roles:', user?.roles);
console.log('Has admin:', user?.roles?.includes('admin'));
```

**Solutions**:
1. If `roles` is undefined → JWT not decoded properly, check authService.js
2. If "admin" not in array → Promote user in database
3. If user is null → Not logged in

---

#### Issue: "403 Forbidden on API calls"
**Diagnosis**:
```bash
# Check backend logs
docker logs analytics-service --tail 50

# Check JWT token
# Decode at https://jwt.io/
```

**Solutions**:
1. Verify JWT includes admin role in payload
2. Check AUTH_SECRET_KEY matches between services
3. Verify require_admin() dependency in backend

---

#### Issue: "Dashboard shows no data"
**Diagnosis**:
```bash
# Check analytics database
docker exec -it analytics-service sqlite3 /app/data/analytics.db
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM messages;
.quit
```

**Solutions**:
1. If tables empty → Use app to generate data
2. If tables don't exist → Run migrations
3. Track activity manually via API docs

---

### 📝 Test Results Template

```markdown
## Analytics Dashboard Test Results

**Date**: [Date]
**Tester**: [Your Name]
**Environment**: Local Docker

| Test Case | Status | Notes |
|-----------|--------|-------|
| 1. Admin Access | ✅/❌ | |
| 2. Non-Admin Block | ✅/❌ | |
| 3. Authentication Flow | ✅/❌ | |
| 4. JWT Token & Roles | ✅/❌ | |
| 5. API Communication | ✅/❌ | |
| 6. Data Display | ✅/❌ | |
| 7. Error Handling | ✅/❌ | |

**Overall Status**: ✅ PASS / ❌ FAIL

**Issues Found**:
- [Issue 1]
- [Issue 2]

**Recommendations**:
- [Recommendation 1]
- [Recommendation 2]
```

---

## Quick Commands Reference

```bash
# Check container status
docker-compose ps

# View frontend logs
docker logs chat-frontend --tail 50 -f

# View analytics logs
docker logs analytics-service --tail 50 -f

# Restart services
docker-compose restart

# Rebuild frontend
docker-compose up -d --build chat-frontend

# Access auth database
docker exec -it auth-server sqlite3 /app/data/app.db

# Access analytics database
docker exec -it analytics-service sqlite3 /app/data/analytics.db

# Clear browser data (console)
localStorage.clear()
location.reload()
```

---

## Success Criteria Summary

✅ **All tests pass**  
✅ **Admin users can access dashboard**  
✅ **Non-admin users blocked**  
✅ **JWT roles extracted correctly**  
✅ **API calls authenticated**  
✅ **Data displays accurately**  
✅ **Errors handled gracefully**  
✅ **No console errors**  

---

**Ready to test? Start with Test 1: Admin Login & Dashboard Access**
