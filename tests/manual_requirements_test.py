"""
Manual Test Script - Key Requirements Verification

This script performs manual tests of critical functionality to verify all requirements are met.
"""

import requests
import time
from datetime import datetime

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
CHAT_SERVICE_URL = "http://localhost:8000"
ANALYTICS_SERVICE_URL = "http://localhost:8002"


def print_test(test_name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"     {message}")


def main():
    print("\n" + "="*80)
    print(" AI Chat Bot - Manual Requirements Verification")
    print("="*80 + "\n")
    
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Test 1: Service Health Checks
    print("="*80)
    print(" Service Health Checks")
    print("="*80)
    
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/health", timeout=5)
        passed = response.status_code == 200
        print_test("Auth Service Health", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Auth Service Health", False, f"Error: {e}")
        results.append(False)
    
    try:
        response = requests.get(f"{CHAT_SERVICE_URL}/health", timeout=5)
        passed = response.status_code == 200
        print_test("Chat Service Health", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Chat Service Health", False, f"Error: {e}")
        results.append(False)
    
    try:
        response = requests.get(f"{ANALYTICS_SERVICE_URL}/health", timeout=5)
        passed = response.status_code == 200
        print_test("Analytics Service Health", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Analytics Service Health", False, f"Error: {e}")
        results.append(False)
    
    # Test 2: Admin Authentication
    print("\n" + "="*80)
    print(" Admin Authentication")
    print("="*80)
    
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data, timeout=5)
        passed = response.status_code == 200
        print_test("Admin Login", passed, f"Status: {response.status_code}")
        
        if passed:
            admin_token = response.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            results.append(True)
        else:
            admin_headers = None
            results.append(False)
    except Exception as e:
        print_test("Admin Login", False, f"Error: {e}")
        admin_headers = None
        results.append(False)
    
    if not admin_headers:
        print("\n❌ Cannot continue without admin authentication")
        return
    
    # Test 3: User Registration
    print("\n" + "="*80)
    print(" User Registration & Authentication")
    print("="*80)
    
    timestamp = int(time.time())
    test_username = f"testuser_{timestamp}"
    test_password = "TestPass123!"
    test_email = f"{test_username}@test.com"
    
    try:
        register_data = {
            "username": test_username,
            "email": test_email,
            "password": test_password
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data, timeout=5)
        passed = response.status_code == 200
        print_test("User Registration", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("User Registration", False, f"Error: {e}")
        results.append(False)
        return
    
    # Test 4: User Login
    try:
        login_data = {"username": test_username, "password": test_password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data, timeout=5)
        passed = response.status_code == 200
        print_test("User Login", passed, f"Status: {response.status_code}")
        
        if passed:
            user_token = response.json()["access_token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            results.append(True)
        else:
            user_headers = None
            results.append(False)
    except Exception as e:
        print_test("User Login", False, f"Error: {e}")
        user_headers = None
        results.append(False)
        return
    
    # Test 5: Conversation Management
    print("\n" + "="*80)
    print(" Conversation Management")
    print("="*80)
    
    try:
        conv_data = {"title": "Test Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{test_username}/conversations/",
            json=conv_data,
            headers=user_headers,
            timeout=5
        )
        passed = response.status_code == 200
        print_test("Create Conversation", passed, f"Status: {response.status_code}")
        
        if passed:
            conversation_id = response.json()["id"]
            results.append(True)
        else:
            conversation_id = None
            results.append(False)
    except Exception as e:
        print_test("Create Conversation", False, f"Error: {e}")
        conversation_id = None
        results.append(False)
    
    # Test 6: Analytics Dashboard Access
    print("\n" + "="*80)
    print(" Analytics Dashboard (Admin Only)")
    print("="*80)
    
    try:
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=admin_headers,
            timeout=5
        )
        passed = response.status_code == 200
        print_test("Get Analytics Summary", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Get Analytics Summary", False, f"Error: {e}")
        results.append(False)
    
    try:
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=user_headers,
            timeout=5
        )
        passed = response.status_code in [403, 401]  # Should be forbidden for regular user
        print_test("Non-Admin Cannot Access Analytics", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Non-Admin Cannot Access Analytics", False, f"Error: {e}")
        results.append(False)
    
    # Test 7: Admin View All Conversations
    print("\n" + "="*80)
    print(" Admin Conversation Management")
    print("="*80)
    
    try:
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/admin/conversations/",
            headers=admin_headers,
            timeout=5
        )
        passed = response.status_code == 200
        print_test("Admin View All Conversations", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Admin View All Conversations", False, f"Error: {e}")
        results.append(False)
    
    # Test 8: Admin Delete Conversation
    if conversation_id:
        try:
            response = requests.delete(
                f"{CHAT_SERVICE_URL}/api/v1/admin/conversations/{conversation_id}",
                headers=admin_headers,
                timeout=5
            )
            passed = response.status_code == 200
            print_test("Admin Delete Conversation", passed, f"Status: {response.status_code}")
            results.append(passed)
        except Exception as e:
            print_test("Admin Delete Conversation", False, f"Error: {e}")
            results.append(False)
    
    # Test 9: Admin User Management
    print("\n" + "="*80)
    print(" Admin User Management")
    print("="*80)
    
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/users/",
            headers=admin_headers,
            timeout=5
        )
        passed = response.status_code == 200
        print_test("Admin List All Users", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Admin List All Users", False, f"Error: {e}")
        results.append(False)
    
    # Test 10: Admin Delete User
    try:
        response = requests.delete(
            f"{AUTH_SERVICE_URL}/users/{test_username}",
            headers=admin_headers,
            timeout=5
        )
        passed = response.status_code == 200
        print_test("Admin Delete User", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Admin Delete User", False, f"Error: {e}")
        results.append(False)
    
    # Test 11: Verify User Deleted
    try:
        login_data = {"username": test_username, "password": test_password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data, timeout=5)
        passed = response.status_code == 401  # Should fail since user is deleted
        print_test("Deleted User Cannot Login", passed, f"Status: {response.status_code}")
        results.append(passed)
    except Exception as e:
        print_test("Deleted User Cannot Login", False, f"Error: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print(" Test Summary")
    print("="*80)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All requirements verified successfully!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed - please review")
        return 1


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
