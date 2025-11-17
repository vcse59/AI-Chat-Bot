"""
Test suite for Analytics Service

Tests analytics tracking, metrics collection, and dashboard functionality.
"""

import pytest
import requests
import time
from datetime import datetime


# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
CHAT_SERVICE_URL = "http://localhost:8000"
ANALYTICS_SERVICE_URL = "http://localhost:8002"


class TestAnalyticsHealth:
    """Test analytics service health and availability"""
    
    def test_analytics_health(self):
        """Test analytics service health endpoint"""
        response = requests.get(f"{ANALYTICS_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json().get("status") == "healthy"


class TestAnalyticsTracking:
    """Test analytics event tracking"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        # Register and login
        timestamp = int(time.time())
        self.username = f"analytics_user_{timestamp}"
        self.password = "TestPass123!"
        self.email = f"{self.username}@test.com"
        
        # Register
        register_data = {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        assert response.status_code == 200
        
        # Login
        login_data = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_conversation_tracking(self):
        """Test that conversations are tracked in analytics"""
        # Create conversation
        conv_data = {"title": "Analytics Test Conversation"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            json=conv_data,
            headers=self.headers
        )
        assert response.status_code == 200
        conversation_id = response.json()["id"]
        
        # Wait for analytics tracking
        time.sleep(2)
        
        # Check analytics summary
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=self.headers
        )
        assert response.status_code == 200
        summary = response.json()
        assert summary["total_conversations"] >= 1
    
    def test_message_tracking(self):
        """Test that messages are tracked in analytics"""
        # Create conversation
        conv_data = {"title": "Message Tracking Test"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/users/{self.username}/conversations/",
            json=conv_data,
            headers=self.headers
        )
        assert response.status_code == 200
        conversation_id = response.json()["id"]
        
        # Send message
        msg_data = {"content": "Test message"}
        response = requests.post(
            f"{CHAT_SERVICE_URL}/api/v1/conversations/{conversation_id}/messages/",
            json=msg_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Wait for analytics tracking
        time.sleep(2)
        
        # Check analytics summary
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=self.headers
        )
        assert response.status_code == 200
        summary = response.json()
        assert summary["total_messages"] >= 1


class TestAnalyticsDashboard:
    """Test analytics dashboard endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin user for analytics access"""
        # Login as admin
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_summary(self):
        """Test getting analytics summary"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields
        assert "total_users" in data
        assert "total_conversations" in data
        assert "total_messages" in data
        assert "active_conversations" in data
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_conversations"], int)
    
    def test_get_metrics_by_role(self):
        """Test getting metrics grouped by role"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/metrics/by-role",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check structure if data exists
        if len(data) > 0:
            assert "role" in data[0]
            assert "total_users" in data[0]
            assert "total_conversations" in data[0]
            assert "total_messages" in data[0]
    
    def test_get_user_metrics(self):
        """Test getting detailed user metrics"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/users/detailed-metrics",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check structure if data exists
        if len(data) > 0:
            assert "username" in data[0]
            assert "total_conversations" in data[0]
            assert "total_messages" in data[0]
            assert "total_tokens" in data[0]
    
    def test_get_top_users(self):
        """Test getting top users by activity"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/users/top?limit=5",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_get_user_activities(self):
        """Test getting recent user activities"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/users/activities?limit=10",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_conversations_list(self):
        """Test getting conversations list in analytics"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/conversations?limit=50",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_token_usage(self):
        """Test getting token usage by conversation"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/tokens/by-conversation?limit=50",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_response_times(self):
        """Test getting response times by user"""
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/response-times/by-user?limit=50",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_non_admin_cannot_access_analytics(self):
        """Test that non-admin users cannot access analytics"""
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
        
        # Login as regular user
        login_data = {"username": username, "password": password}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access analytics
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=headers
        )
        # Should be forbidden or redirect
        assert response.status_code in [403, 401]


class TestAnalyticsSilentUpdates:
    """Test silent background updates in analytics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin user"""
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/token", data=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_analytics_returns_quickly(self):
        """Test that analytics endpoints return quickly for silent updates"""
        start_time = time.time()
        
        response = requests.get(
            f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
            headers=self.headers
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should return in less than 1 second
    
    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent analytics requests"""
        import concurrent.futures
        
        def make_request():
            return requests.get(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/summary",
                headers=self.headers
            )
        
        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
