"""
Test suite for Admin Features

Tests admin-only functionality including conversation management, user deletion,
and admin-specific endpoints.
"""

import pytest
import requests
import time


# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
CHAT_SERVICE_URL = "http://localhost:8000"
ANALYTICS_SERVICE_URL = "http://localhost:8002"


class TestAdminConversationManagement:
    """Test admin's ability to manage all conversations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin and regular users"""
        # Login as admin
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        assert response.status_code == 200
        self.admin_token = response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create regular user
        timestamp = int(time.time())
        self.regular_username = f"user_{timestamp}"
        self.regular_password = "TestPass123!"
        
        register_data = {
            "username": self.regular_username,
            "email": f"{self.regular_username}@test.com",
            "password": self.regular_password
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        assert response.status_code == 200
        
        # Login as regular user
        login_data = {"username": self.regular_username, "password": self.regular_password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        assert response.status_code == 200
        self.user_token = response.json()["access_token"]
        self.user_headers = {"Authorization": f"Bearer {self.user_token}"}
    
    def test_admin_can_view_all_conversations(self):
        """Test that admin can view all conversations from all users"""
        # User creates conversation
        conv_data = {"title": "User's Private Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.regular_username}/conversations/",
            json=conv_data,
            headers=self.user_headers
        )
        assert response.status_code == 200
        conversation_id = response.json()["id"]
        
        # Admin views all conversations
        response = requests.get(
            f"{CHAT_SERVICE_URL}/admin/conversations/",
            headers=self.admin_headers
        )
        assert response.status_code == 200
        conversations = response.json()
        
        # Should include user's conversation
        conv_ids = [c["id"] for c in conversations]
        assert conversation_id in conv_ids
    
    def test_admin_can_delete_any_conversation(self):
        """Test that admin can delete conversations from any user"""
        # User creates conversation
        conv_data = {"title": "Conversation to be deleted by admin"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.regular_username}/conversations/",
            json=conv_data,
            headers=self.user_headers
        )
        assert response.status_code == 200
        conversation_id = response.json()["id"]
        
        # Admin deletes conversation
        response = requests.delete(
            f"{CHAT_SERVICE_URL}/admin/conversations/{conversation_id}",
            headers=self.admin_headers
        )
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify conversation is deleted
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{conversation_id}",
            headers=self.user_headers
        )
        assert response.status_code == 404
    
    def test_regular_user_cannot_delete_others_conversation(self):
        """Test that regular users cannot delete other users' conversations"""
        # Create second user
        timestamp = int(time.time())
        username2 = f"user2_{timestamp}"
        password2 = "TestPass123!"
        
        register_data = {
            "username": username2,
            "email": f"{username2}@test.com",
            "password": password2
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        login_data = {"username": username2, "password": password2}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        token2 = response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User2 creates conversation
        conv_data = {"title": "User2's conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{username2}/conversations/",
            json=conv_data,
            headers=headers2
        )
        conversation_id = response.json()["id"]
        
        # User1 tries to delete User2's conversation
        response = requests.delete(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{conversation_id}",
            headers=self.user_headers
        )
        # Should be forbidden or not found
        assert response.status_code in [403, 404]
    
    def test_non_admin_cannot_access_admin_endpoints(self):
        """Test that regular users cannot access admin endpoints"""
        # Try to get all conversations (admin endpoint)
        response = requests.get(
            f"{CHAT_SERVICE_URL}/admin/conversations/",
            headers=self.user_headers
        )
        assert response.status_code == 403
        
        # Try to delete via admin endpoint
        response = requests.delete(
            f"{CHAT_SERVICE_URL}/admin/conversations/fake-id",
            headers=self.user_headers
        )
        assert response.status_code == 403


class TestAdminUserManagement:
    """Test admin's ability to manage users"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin user"""
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        assert response.status_code == 200
        self.admin_token = response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_can_list_all_users(self):
        """Test that admin can list all users"""
        response = requests.get(
            f"{AUTH_SERVICE_URL}/users/",
            headers=self.admin_headers
        )
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1  # At least admin user
        
        # Check structure
        if len(users) > 0:
            assert "username" in users[0]
            assert "email" in users[0]
    
    def test_admin_can_delete_user(self):
        """Test that admin can delete users"""
        # Create test user
        timestamp = int(time.time())
        username = f"deleteme_{timestamp}"
        password = "TestPass123!"
        
        register_data = {
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        assert response.status_code == 200
        
        # Admin deletes user
        response = requests.delete(
            f"{AUTH_SERVICE_URL}/users/{username}",
            headers=self.admin_headers
        )
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify user cannot login
        login_data = {"username": username, "password": password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        assert response.status_code == 401
    
    def test_admin_cannot_delete_nonexistent_user(self):
        """Test deleting non-existent user returns 404"""
        response = requests.delete(
            f"{AUTH_SERVICE_URL}/users/nonexistent_user_12345",
            headers=self.admin_headers
        )
        assert response.status_code == 404
    
    def test_regular_user_cannot_delete_users(self):
        """Test that regular users cannot delete other users"""
        # Create two users
        timestamp = int(time.time())
        user1 = f"user1_{timestamp}"
        user2 = f"user2_{timestamp}"
        password = "TestPass123!"
        
        for username in [user1, user2]:
            register_data = {
                "username": username,
                "email": f"{username}@test.com",
                "password": password
            }
            requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        # Login as user1
        login_data = {"username": user1, "password": password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to delete user2
        response = requests.delete(
            f"{AUTH_SERVICE_URL}/users/{user2}",
            headers=headers
        )
        assert response.status_code == 403


class TestAdminRoleManagement:
    """Test admin role creation and management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin user"""
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.admin_token = response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_can_list_roles(self):
        """Test that admin can list all roles"""
        response = requests.get(
            f"{AUTH_SERVICE_URL}/roles/",
            headers=self.admin_headers
        )
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        
        # Should have default roles
        role_names = [r["name"] for r in roles]
        assert "admin" in role_names
        assert "user" in role_names
    
    def test_admin_can_create_role(self):
        """Test that admin can create new roles"""
        timestamp = int(time.time())
        role_data = {
            "name": f"test_role_{timestamp}",
            "description": "Test role for testing"
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/roles/",
            json=role_data,
            headers=self.admin_headers
        )
        
        # May already exist or be created
        assert response.status_code in [200, 400]
    
    def test_regular_user_cannot_manage_roles(self):
        """Test that regular users cannot manage roles"""
        # Create regular user
        timestamp = int(time.time())
        username = f"regular_{timestamp}"
        password = "TestPass123!"
        
        register_data = {
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        # Login
        login_data = {"username": username, "password": password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to create role
        role_data = {"name": "unauthorized_role", "description": "Test"}
        response = requests.post(
            f"{AUTH_SERVICE_URL}/roles/",
            json=role_data,
            headers=headers
        )
        assert response.status_code == 403


class TestAdminRegistration:
    """Test admin user registration"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin user"""
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.admin_token = response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_can_register_new_admin(self):
        """Test that admin can register other admins"""
        timestamp = int(time.time())
        admin_data = {
            "username": f"newadmin_{timestamp}",
            "email": f"newadmin_{timestamp}@test.com",
            "password": "AdminPass123!"
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/register-admin",
            json=admin_data,
            headers=self.admin_headers
        )
        assert response.status_code == 200
        
        # Verify new admin can login
        login_data = {
            "username": admin_data["username"],
            "password": admin_data["password"]
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        assert response.status_code == 200
        
        # Verify has admin role
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{AUTH_SERVICE_URL}/users/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        role_names = [r["name"] for r in user_data.get("roles", [])]
        assert "admin" in role_names
    
    def test_regular_user_cannot_register_admin(self):
        """Test that regular users cannot register admins"""
        # Create regular user
        timestamp = int(time.time())
        username = f"regular_{timestamp}"
        password = "TestPass123!"
        
        register_data = {
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        # Login
        login_data = {"username": username, "password": password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to register admin
        admin_data = {
            "username": f"unauthorized_admin_{timestamp}",
            "email": f"unauthorized_admin_{timestamp}@test.com",
            "password": "AdminPass123!"
        }
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/register-admin",
            json=admin_data,
            headers=headers
        )
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
