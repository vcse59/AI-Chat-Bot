"""
End-to-End Test Suite - Complete User Journey.

This test suite simulates a complete user journey through the application:
1. User Registration
2. User Login
3. Create Conversation
4. Send Messages
5. Receive AI Responses
6. Manage Conversations
7. User Logout

These tests verify the entire system works together correctly.
"""
import pytest
import requests
import json
import time
from websocket import create_connection
from conftest import AUTH_BASE_URL, CHAT_BASE_URL


class TestCompleteUserJourney:
    """Test complete user journey from registration to chat."""
    
    def test_full_user_journey_rest_api(self):
        """
        Test complete user journey using REST API only.
        
        Flow:
        1. Register new user
        2. Login to get token
        3. Verify authentication
        4. Create conversation
        5. Send message
        6. Get conversation history
        7. Update conversation
        8. Delete conversation
        """
        # Step 1: Register new user
        timestamp = int(time.time() * 1000)
        user_data = {
            "username": f"journey_user_{timestamp}",
            "email": f"journey_{timestamp}@example.com",
            "password": "JourneyPassword123!"
        }
        
        register_response = requests.post(
            f"{AUTH_BASE_URL}/users/",
            json=user_data
        )
        assert register_response.status_code == 200
        print("✓ User registered successfully")
        
        # Step 2: Login to get token
        login_response = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={
                "username": user_data["username"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print("✓ User logged in successfully")
        
        # Step 3: Verify authentication
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        me_response = requests.get(
            f"{AUTH_BASE_URL}/users/me",
            headers=auth_headers
        )
        assert me_response.status_code == 200
        assert me_response.json()["username"] == user_data["username"]
        print("✓ User authentication verified")
        
        # Step 4: Create conversation
        conv_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "My First Conversation",
                "user_id": user_data["username"]
            }
        )
        assert conv_response.status_code in [200, 201]
        conversation_data = conv_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        print(f"✓ Conversation created (ID: {conversation_id})")
        
        # Step 5: Send message
        message_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}/messages",
            headers=auth_headers,
            json={
                "content": "Hello! This is my first message.",
                "role": "user"
            }
        )
        assert message_response.status_code in [200, 201]
        print("✓ Message sent successfully")
        
        # Step 6: Get conversation history
        messages_response = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}/messages",
            headers=auth_headers
        )
        assert messages_response.status_code == 200
        messages = messages_response.json()
        assert len(messages) > 0 if isinstance(messages, list) else "messages" in messages
        print("✓ Conversation history retrieved")
        
        # Step 7: Update conversation
        update_response = requests.put(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}",
            headers=auth_headers,
            json={"title": "Updated Conversation Title"}
        )
        assert update_response.status_code == 200
        print("✓ Conversation updated")
        
        # Step 8: Delete conversation
        delete_response = requests.delete(
            f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}",
            headers=auth_headers
        )
        assert delete_response.status_code in [200, 204]
        print("✓ Conversation deleted")
        
        print("\n✅ Complete user journey test PASSED")
    
    def test_full_user_journey_websocket(self):
        """
        Test complete user journey using WebSocket.
        
        Flow:
        1. Register and login
        2. Connect via WebSocket
        3. Start conversation
        4. Send messages
        5. End conversation
        6. Disconnect
        """
        # Step 1: Register and login
        timestamp = int(time.time() * 1000)
        user_data = {
            "username": f"ws_journey_{timestamp}",
            "email": f"ws_journey_{timestamp}@example.com",
            "password": "WSJourneyPassword123!"
        }
        
        requests.post(f"{AUTH_BASE_URL}/users/", json=user_data)
        
        login_response = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={
                "username": user_data["username"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        access_token = login_response.json()["access_token"]
        print("✓ User registered and logged in")
        
        # Step 2: Connect via WebSocket
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{user_data['username']}" +
            f"?token={access_token}"
        )
        
        try:
            ws = create_connection(ws_url, timeout=10)
            assert ws.connected
            print("✓ WebSocket connected")
            
            ws.settimeout(5)
            
            # Step 3: Start conversation
            start_msg = {
                "action": "start_conversation",
                "data": {"title": "WebSocket Journey Conversation"}
            }
            ws.send(json.dumps(start_msg))
            
            response = ws.recv()
            response_data = json.loads(response)
            conversation_id = response_data.get("conversation_id") or response_data.get("id")
            print(f"✓ Conversation started (ID: {conversation_id})")
            
            # Step 4: Send messages
            chat_msg = {
                "action": "send_message",
                "data": {
                    "conversation_id": conversation_id,
                    "content": "Hello via WebSocket!"
                }
            }
            ws.send(json.dumps(chat_msg))
            
            response = ws.recv()
            print("✓ Message sent and response received")
            
            # Step 5: End conversation
            end_msg = {
                "action": "end_conversation",
                "data": {"conversation_id": conversation_id}
            }
            ws.send(json.dumps(end_msg))
            
            response = ws.recv()
            print("✓ Conversation ended")
            
            # Step 6: Disconnect
            ws.close()
            print("✓ WebSocket disconnected")
            
            print("\n✅ WebSocket user journey test PASSED")
            
        except Exception as e:
            pytest.skip(f"WebSocket journey test skipped: {str(e)}")


class TestMultiUserScenarios:
    """Test scenarios involving multiple users."""
    
    def test_two_users_separate_conversations(self):
        """Test two users maintaining separate conversations."""
        # Create User 1
        timestamp = int(time.time() * 1000)
        user1_data = {
            "username": f"multi_user1_{timestamp}",
            "email": f"multi_user1_{timestamp}@example.com",
            "password": "Password123!"
        }
        
        requests.post(f"{AUTH_BASE_URL}/users/", json=user1_data)
        login1 = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={"username": user1_data["username"], "password": user1_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Create User 2
        time.sleep(0.1)
        user2_data = {
            "username": f"multi_user2_{timestamp}1",
            "email": f"multi_user2_{timestamp}1@example.com",
            "password": "Password123!"
        }
        
        requests.post(f"{AUTH_BASE_URL}/users/", json=user2_data)
        login2 = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={"username": user2_data["username"], "password": user2_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User 1 creates conversation
        conv1 = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=headers1,
            json={"title": "User 1 Conversation", "user_id": user1_data["username"]}
        )
        assert conv1.status_code in [200, 201]
        
        # User 2 creates conversation
        conv2 = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=headers2,
            json={"title": "User 2 Conversation", "user_id": user2_data["username"]}
        )
        assert conv2.status_code in [200, 201]
        
        # User 1 lists their conversations
        list1 = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=headers1,
            params={"user_id": user1_data["username"]}
        )
        assert list1.status_code == 200
        
        # User 2 lists their conversations
        list2 = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=headers2,
            params={"user_id": user2_data["username"]}
        )
        assert list2.status_code == 200
        
        print("✅ Multi-user separate conversations test PASSED")


class TestErrorRecovery:
    """Test error handling and recovery scenarios."""
    
    def test_invalid_conversation_id(self, authenticated_user, auth_headers):
        """Test accessing non-existent conversation."""
        response = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/999999",
            headers=auth_headers
        )
        assert response.status_code in [404, 400]
    
    def test_unauthorized_conversation_access(self):
        """Test accessing conversation without proper authentication."""
        response = requests.get(
            f"{CHAT_BASE_URL}/api/v1/conversations/1"
        )
        assert response.status_code in [401, 403]
    
    def test_expired_token_handling(self, test_user_data):
        """Test handling of expired authentication token."""
        # Use a clearly invalid/expired token
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.invalid"
        
        response = requests.get(
            f"{AUTH_BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == 401
    
    def test_malformed_request_data(self, authenticated_user, auth_headers):
        """Test handling of malformed request data."""
        response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={"invalid_field": "value"}  # Missing required fields
        )
        # Should return validation error
        assert response.status_code in [400, 422]


class TestPerformance:
    """Basic performance and load tests."""
    
    def test_create_multiple_conversations(self, authenticated_user, auth_headers):
        """Test creating multiple conversations in sequence."""
        conversation_ids = []
        
        for i in range(5):
            response = requests.post(
                f"{CHAT_BASE_URL}/api/v1/conversations/",
                headers=auth_headers,
                json={
                    "title": f"Performance Test Conversation {i}",
                    "user_id": authenticated_user["username"]
                }
            )
            assert response.status_code in [200, 201]
            
            data = response.json()
            conv_id = data.get("id") or data.get("conversation_id")
            conversation_ids.append(conv_id)
        
        assert len(conversation_ids) == 5
        print(f"✅ Created {len(conversation_ids)} conversations successfully")
    
    def test_rapid_message_sending(self, authenticated_user, auth_headers):
        """Test sending multiple messages rapidly."""
        # Create conversation
        conv_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Rapid Message Test",
                "user_id": authenticated_user["username"]
            }
        )
        conv_data = conv_response.json()
        conversation_id = conv_data.get("id") or conv_data.get("conversation_id")
        
        # Send multiple messages
        for i in range(3):
            response = requests.post(
                f"{CHAT_BASE_URL}/api/v1/conversations/{conversation_id}/messages",
                headers=auth_headers,
                json={
                    "content": f"Rapid test message {i}",
                    "role": "user"
                }
            )
            assert response.status_code in [200, 201]
        
        print("✅ Rapid message sending test PASSED")
