"""
Test suite for OpenAI ChatBot API Service.

Tests cover:
- Conversation management
- Message handling
- API authentication integration
- Chat service health
"""
import pytest
import requests
from conftest import CHAT_BASE_URL


class TestConversationManagement:
    """Test conversation CRUD operations."""
    
    def test_create_conversation(self, authenticated_user, auth_headers):
        """Test creating a new conversation."""
        response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Test Conversation",
                "user_id": authenticated_user["username"]
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "conversation_id" in data
    
    def test_list_conversations(self, authenticated_user, auth_headers):
        """Test listing user's conversations."""
        # Create a conversation first
        requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Test Conversation for Listing",
                "user_id": authenticated_user["username"]
            }
        )
        
        # List conversations
        response = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            params={"user_id": authenticated_user["username"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "conversations" in data
    
    def test_get_conversation_by_id(self, authenticated_user, auth_headers):
        """Test retrieving a specific conversation."""
        # Create a conversation
        create_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Get Conversation Test",
                "user_id": authenticated_user["username"]
            }
        )
        
        assert create_response.status_code in [200, 201]
        conversation_data = create_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        
        # Get the conversation
        response = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == conversation_id or data.get("conversation_id") == conversation_id
    
    def test_update_conversation(self, authenticated_user, auth_headers):
        """Test updating conversation title."""
        # Create a conversation
        create_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Original Title",
                "user_id": authenticated_user["username"]
            }
        )
        
        conversation_data = create_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        
        # Update the conversation
        response = requests.put(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}",
            headers=auth_headers,
            json={"title": "Updated Title"}
        )
        
        assert response.status_code == 200
    
    def test_delete_conversation(self, authenticated_user, auth_headers):
        """Test deleting a conversation."""
        # Create a conversation
        create_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "To Be Deleted",
                "user_id": authenticated_user["username"]
            }
        )
        
        conversation_data = create_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        
        # Delete the conversation
        response = requests.delete(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204]
    
    def test_create_conversation_without_auth(self, test_user_data):
        """Test creating conversation without authentication fails."""
        response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            json={
                "title": "Unauthorized Conversation",
                "user_id": test_user_data["username"]
            }
        )
        
        # Should fail without authentication
        assert response.status_code in [401, 403]


class TestMessageHandling:
    """Test message operations within conversations."""
    
    def test_send_message_to_conversation(self, authenticated_user, auth_headers):
        """Test sending a message to a conversation."""
        # Create a conversation first
        conv_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Message Test Conversation",
                "user_id": authenticated_user["username"]
            }
        )
        
        conversation_data = conv_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        
        # Send a message
        response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}/messages",
            headers=auth_headers,
            json={
                "content": "Hello, this is a test message!",
                "role": "user"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "message_id" in data
    
    def test_get_conversation_messages(self, authenticated_user, auth_headers):
        """Test retrieving messages from a conversation."""
        # Create conversation
        conv_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Get Messages Test",
                "user_id": authenticated_user["username"]
            }
        )
        
        conversation_data = conv_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        
        # Send a message
        requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}/messages",
            headers=auth_headers,
            json={
                "content": "Test message for retrieval",
                "role": "user"
            }
        )
        
        # Get messages
        response = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "messages" in data
    
    def test_send_message_without_auth(self):
        """Test sending message without authentication fails."""
        response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/1/messages",
            json={
                "content": "Unauthorized message",
                "role": "user"
            }
        )
        
        assert response.status_code in [401, 403]


class TestChatServiceHealth:
    """Test chat service health and configuration."""
    
    def test_health_endpoint(self):
        """Test chat service health check."""
        response = requests.get(f"{CHAT_BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test chat service root endpoint returns API info."""
        response = requests.get(f"{CHAT_BASE_URL}/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "version" in data
    
    def test_chat_health_endpoint(self):
        """Test dedicated chat health endpoint."""
        response = requests.get(f"{CHAT_BASE_URL}/api/v1/chat/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "chat_service" in data
        assert data["chat_service"] == "active"


class TestUserIsolation:
    """Test that users can only access their own conversations."""
    
    def test_user_cannot_access_other_conversations(self, admin_user, admin_headers):
        """Test user isolation - users should not see other users' conversations."""
        # Create two different authenticated users
        import time
        
        # User 1
        user1_data = {
            "username": f"user1_{int(time.time() * 1000)}",
            "email": f"user1_{int(time.time() * 1000)}@example.com",
            "password": "Password123!"
        }
        
        requests.post(
            f"{CHAT_BASE_URL.replace('8000', '8001')}/users/",
            json=user1_data
        )
        
        login_response = requests.post(
            f"{CHAT_BASE_URL.replace('8000', '8001')}/auth/token",
            data={
                "username": user1_data["username"],
                "password": user1_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        user1_token = login_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        # User 2
        time.sleep(0.1)  # Ensure different timestamp
        user2_data = {
            "username": f"user2_{int(time.time() * 1000)}",
            "email": f"user2_{int(time.time() * 1000)}@example.com",
            "password": "Password123!"
        }
        
        requests.post(
            f"{CHAT_BASE_URL.replace('8000', '8001')}/users/",
            json=user2_data
        )
        
        login_response = requests.post(
            f"{CHAT_BASE_URL.replace('8000', '8001')}/auth/token",
            data={
                "username": user2_data["username"],
                "password": user2_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User 1 creates a conversation
        conv_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=user1_headers,
            json={
                "title": "User 1 Private Conversation",
                "user_id": user1_data["username"]
            }
        )
        
        # User 2 lists conversations - should not see User 1's conversation
        response = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=user2_headers,
            params={"user_id": user2_data["username"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        conversations = data if isinstance(data, list) else data.get("conversations", [])
        
        # User 2 should have no conversations or none from User 1
        user1_conv_titles = [c.get("title") for c in conversations]
        assert "User 1 Private Conversation" not in user1_conv_titles
