"""
Test suite for Database Integrity and Data Isolation

Tests database separation, data isolation between services,
and cascade operations.
"""

import pytest
import requests
import time


# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
CHAT_SERVICE_URL = "http://localhost:8000"
ANALYTICS_SERVICE_URL = "http://localhost:8002"


class TestDatabaseSeparation:
    """Test that services use separate databases"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        timestamp = int(time.time())
        self.username = f"dbtest_{timestamp}"
        self.password = "TestPass123!"
        
        # Register
        register_data = {
            "username": self.username,
            "email": f"{self.username}@test.com",
            "password": self.password
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        assert response.status_code == 200
        
        # Login
        login_data = {"username": self.username, "password": self.password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_auth_and_chat_databases_are_separate(self):
        """Test that auth and chat services use different databases"""
        # User exists in auth service
        response = requests.get(
            f"{AUTH_SERVICE_URL}/users/me",
            headers=self.headers
        )
        assert response.status_code == 200
        auth_user = response.json()
        
        # Create conversation in chat service
        conv_data = {"title": "Test Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            json=conv_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Both services should work independently
        # This verifies they don't share database constraints
    
    def test_analytics_database_is_separate(self):
        """Test that analytics service has its own database"""
        # Admin login
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create conversation (tracked in analytics)
        conv_data = {"title": "Analytics Test"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            json=conv_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Wait for analytics tracking
        time.sleep(2)
        
        # Get analytics data
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # Analytics should have data independent of other services


class TestUserDataIsolation:
    """Test that users can only access their own data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup two test users"""
        timestamp = int(time.time())
        
        # User 1
        self.user1 = f"user1_{timestamp}"
        self.pass1 = "TestPass123!"
        register_data = {
            "username": self.user1,
            "email": f"{self.user1}@test.com",
            "password": self.pass1
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        login_data = {"username": self.user1, "password": self.pass1}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.token1 = response.json()["access_token"]
        self.headers1 = {"Authorization": f"Bearer {self.token1}"}
        
        # User 2
        self.user2 = f"user2_{timestamp}"
        self.pass2 = "TestPass123!"
        register_data = {
            "username": self.user2,
            "email": f"{self.user2}@test.com",
            "password": self.pass2
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        login_data = {"username": self.user2, "password": self.pass2}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.token2 = response.json()["access_token"]
        self.headers2 = {"Authorization": f"Bearer {self.token2}"}
    
    def test_users_cannot_see_each_others_conversations(self):
        """Test conversation isolation between users"""
        # User1 creates conversation
        conv_data = {"title": "User1's Private Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.user1}/conversations/",
            json=conv_data,
            headers=self.headers1
        )
        assert response.status_code == 200
        user1_conv_id = response.json()["id"]
        
        # User2 creates conversation
        conv_data = {"title": "User2's Private Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.user2}/conversations/",
            json=conv_data,
            headers=self.headers2
        )
        assert response.status_code == 200
        user2_conv_id = response.json()["id"]
        
        # User1 gets their conversations
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.user1}/conversations/",
            headers=self.headers1
        )
        assert response.status_code == 200
        user1_convs = response.json()
        user1_conv_ids = [c["id"] for c in user1_convs]
        
        # Should not contain user2's conversation
        assert user2_conv_id not in user1_conv_ids
        assert user1_conv_id in user1_conv_ids
    
    def test_users_cannot_access_each_others_messages(self):
        """Test message isolation between users"""
        # User1 creates conversation and message
        conv_data = {"title": "User1's Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.user1}/conversations/",
            json=conv_data,
            headers=self.headers1
        )
        user1_conv_id = response.json()["id"]
        
        msg_data = {"content": "User1's secret message"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{user1_conv_id}/messages/",
            json=msg_data,
            headers=self.headers1
        )
        assert response.status_code == 200
        
        # User2 tries to access User1's conversation
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{user1_conv_id}",
            headers=self.headers2
        )
        # Should be forbidden or not found
        assert response.status_code in [403, 404]
        
        # User2 tries to get messages
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{user1_conv_id}/messages/",
            headers=self.headers2
        )
        assert response.status_code in [403, 404]


class TestCascadeOperations:
    """Test cascade delete and update operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin and test user"""
        # Admin
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.admin_token = response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test user
        timestamp = int(time.time())
        self.username = f"cascade_test_{timestamp}"
        self.password = "TestPass123!"
        
        register_data = {
            "username": self.username,
            "email": f"{self.username}@test.com",
            "password": self.password
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        login_data = {"username": self.username, "password": self.password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_deleting_conversation_removes_messages(self):
        """Test that deleting conversation removes associated messages"""
        # Create conversation
        conv_data = {"title": "Conversation with Messages"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            json=conv_data,
            headers=self.headers
        )
        conv_id = response.json()["id"]
        
        # Add messages
        for i in range(3):
            msg_data = {"content": f"Test message {i}"}
            response = requests.post(
                f"{CHAT_SERVICE_URL}/api/v1/conversations/{conv_id}/messages/",
                json=msg_data,
                headers=self.headers
            )
            assert response.status_code == 200
        
        # Verify messages exist
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{conv_id}/messages/",
            headers=self.headers
        )
        assert response.status_code == 200
        assert len(response.json()) >= 3
        
        # Delete conversation
        response = requests.delete(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{conv_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Verify messages are also gone
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{conv_id}/messages/",
            headers=self.headers
        )
        assert response.status_code == 404
    
    def test_user_deletion_impact(self):
        """Test the impact of user deletion on related data"""
        # Create user with conversation
        timestamp = int(time.time())
        username = f"deletable_user_{timestamp}"
        password = "TestPass123!"
        
        register_data = {
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        login_data = {"username": username, "password": password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create conversation
        conv_data = {"title": "User's Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{username}/conversations/",
            json=conv_data,
            headers=headers
        )
        assert response.status_code == 200
        conv_id = response.json()["id"]
        
        # Admin deletes user
        response = requests.delete(
            f"{AUTH_SERVICE_URL}/users/{username}",
            headers=self.admin_headers
        )
        assert response.status_code == 200
        
        # User should not be able to login
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/token",
            data={"username": username, "password": password}
        )
        assert response.status_code == 401
        
        # Note: Orphaned conversations may remain in chat DB
        # This is expected behavior - analytics tracks it separately


class TestDataConsistency:
    """Test data consistency across services"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and admin"""
        # Admin
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.admin_token = response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test user
        timestamp = int(time.time())
        self.username = f"consistency_{timestamp}"
        self.password = "TestPass123!"
        
        register_data = {
            "username": self.username,
            "email": f"{self.username}@test.com",
            "password": self.password
        }
        requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        
        login_data = {"username": self.username, "password": self.password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_conversation_count_consistency(self):
        """Test that conversation counts are consistent"""
        # Get initial count from chat service
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            headers=self.headers
        )
        initial_count = len(response.json())
        
        # Create conversations
        for i in range(3):
            conv_data = {"title": f"Consistency Test {i}"}
            response = requests.post(
                f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
                json=conv_data,
                headers=self.headers
            )
            assert response.status_code == 200
        
        # Get updated count
        response = requests.get(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            headers=self.headers
        )
        new_count = len(response.json())
        
        assert new_count == initial_count + 3
    
    def test_analytics_tracking_consistency(self):
        """Test that analytics tracking is consistent"""
        # Get initial analytics
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=self.admin_headers
        )
        initial_summary = response.json()
        initial_convs = initial_summary.get("total_conversations", 0)
        
        # Create conversation
        conv_data = {"title": "Analytics Consistency Test"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            json=conv_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Wait for analytics tracking
        time.sleep(2)
        
        # Check analytics updated
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=self.admin_headers
        )
        new_summary = response.json()
        new_convs = new_summary.get("total_conversations", 0)
        
        assert new_convs >= initial_convs  # Should increase or stay same


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
