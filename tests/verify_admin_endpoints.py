"""
Quick verification script for admin conversation endpoints
"""
import requests
import time

BASE_URL = "http://localhost:8000"

print("=" * 80)
print(" Admin Endpoints Verification")
print("=" * 80)
print()

# Wait a moment for services to be ready
print("Waiting for services to be ready...")
time.sleep(3)

# 1. Get admin token
print("1. Getting admin token...")
try:
    response = requests.post(
        f"http://localhost:8001/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        admin_token = response.json()["access_token"]
        print(f"   ✅ Admin token obtained")
    else:
        print(f"   ❌ Failed to get admin token: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error getting admin token: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {admin_token}"}

# 2. Test GET /api/v1/admin/conversations/
print("\n2. Testing GET /api/v1/admin/conversations/...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/admin/conversations/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        conversations = response.json()
        print(f"   ✅ PASS - Found {len(conversations)} conversations")
        if conversations:
            print(f"   First conversation ID: {conversations[0].get('id', 'N/A')}")
    else:
        print(f"   ❌ FAIL - Expected 200, got {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 3. Create a test conversation to delete
print("\n3. Creating test conversation...")
try:
    # Register test user
    test_username = f"deletetest_{int(time.time())}"
    response = requests.post(
        "http://localhost:8001/api/v1/users/",
        json={
            "username": test_username,
            "email": f"{test_username}@test.com",
            "password": "testpass123",
            "full_name": "Delete Test User"
        }
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Test user created: {test_username}")
        
        # Login as test user
        response = requests.post(
            "http://localhost:8001/api/v1/auth/login",
            data={"username": test_username, "password": "testpass123"}
        )
        
        if response.status_code == 200:
            user_token = response.json()["access_token"]
            user_id = response.json()["user_id"]
            
            # Create conversation
            response = requests.post(
                f"{BASE_URL}/api/v1/users/{user_id}/conversations/",
                json={"title": "Test Conversation for Admin Delete"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            if response.status_code in [200, 201]:
                conversation_id = response.json()["id"]
                print(f"   ✅ Test conversation created: {conversation_id}")
                
                # 4. Test DELETE with admin
                print(f"\n4. Testing DELETE /api/v1/admin/conversations/{conversation_id}...")
                response = requests.delete(
                    f"{BASE_URL}/api/v1/admin/conversations/{conversation_id}",
                    headers=headers
                )
                print(f"   Status: {response.status_code}")
                if response.status_code in [200, 204]:
                    print(f"   ✅ PASS - Admin successfully deleted conversation")
                else:
                    print(f"   ❌ FAIL - Expected 200/204, got {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print(f"   ❌ Failed to create conversation: {response.status_code}")
        else:
            print(f"   ❌ Failed to login as test user: {response.status_code}")
    else:
        print(f"   ⚠️  User might already exist or creation failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 80)
print(" Verification Complete")
print("=" * 80)
