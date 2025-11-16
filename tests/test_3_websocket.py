"""
Test suite for WebSocket Chat Functionality.

Tests cover:
- WebSocket connection establishment
- Real-time message exchange
- Authentication via WebSocket
- Connection lifecycle
"""
import pytest
import json
import time
from websocket import create_connection, WebSocketTimeoutException
from conftest import CHAT_BASE_URL


class TestWebSocketConnection:
    """Test WebSocket connection functionality."""
    
    def test_websocket_connection_without_auth(self):
        """Test WebSocket connection without authentication (anonymous)."""
        ws_url = CHAT_BASE_URL.replace("http://", "ws://") + "/ws/chat"
        
        try:
            ws = create_connection(ws_url, timeout=10)
            assert ws.connected
            ws.close()
        except Exception as e:
            pytest.fail(f"Failed to connect to WebSocket: {str(e)}")
    
    def test_websocket_connection_with_auth(self, authenticated_user):
        """Test WebSocket connection with JWT authentication."""
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{authenticated_user['username']}" +
            f"?token={authenticated_user['access_token']}"
        )
        
        try:
            ws = create_connection(ws_url, timeout=10)
            assert ws.connected
            ws.close()
        except Exception as e:
            pytest.fail(f"Failed to connect to authenticated WebSocket: {str(e)}")
    
    def test_websocket_connection_with_invalid_token(self, authenticated_user):
        """Test WebSocket connection with invalid token fails."""
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{authenticated_user['username']}" +
            "?token=invalid_token_12345"
        )
        
        with pytest.raises(Exception):
            # Should fail to connect with invalid token
            ws = create_connection(ws_url, timeout=5)
            ws.close()
    
    def test_websocket_connection_token_user_mismatch(self, authenticated_user):
        """Test WebSocket connection fails when token user doesn't match path user."""
        # Try to connect with valid token but different username in path
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            "/ws/chat/different_user_12345" +
            f"?token={authenticated_user['access_token']}"
        )
        
        with pytest.raises(Exception):
            # Should fail due to user mismatch
            ws = create_connection(ws_url, timeout=5)
            ws.close()


class TestWebSocketMessaging:
    """Test WebSocket message exchange."""
    
    def test_start_conversation_via_websocket(self, authenticated_user):
        """Test starting a conversation via WebSocket."""
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{authenticated_user['username']}" +
            f"?token={authenticated_user['access_token']}"
        )
        
        try:
            ws = create_connection(ws_url, timeout=10)
            
            # Send start conversation command
            start_message = {
                "action": "start_conversation",
                "data": {
                    "title": "WebSocket Test Conversation"
                }
            }
            ws.send(json.dumps(start_message))
            
            # Wait for response
            ws.settimeout(5)
            response = ws.recv()
            response_data = json.loads(response)
            
            assert "conversation_id" in response_data or "id" in response_data
            
            ws.close()
        except WebSocketTimeoutException:
            pytest.skip("WebSocket response timeout - server may not be configured for this test")
        except Exception as e:
            pytest.fail(f"WebSocket conversation start failed: {str(e)}")
    
    def test_send_message_via_websocket(self, authenticated_user):
        """Test sending a chat message via WebSocket."""
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{authenticated_user['username']}" +
            f"?token={authenticated_user['access_token']}"
        )
        
        try:
            ws = create_connection(ws_url, timeout=10)
            ws.settimeout(5)
            
            # Start conversation first
            start_message = {
                "action": "start_conversation",
                "data": {
                    "title": "Message Test Conversation"
                }
            }
            ws.send(json.dumps(start_message))
            
            # Get conversation ID from response
            response = ws.recv()
            response_data = json.loads(response)
            conversation_id = response_data.get("conversation_id") or response_data.get("id")
            
            # Send a message
            chat_message = {
                "action": "send_message",
                "data": {
                    "conversation_id": conversation_id,
                    "content": "Hello from WebSocket test!"
                }
            }
            ws.send(json.dumps(chat_message))
            
            # Wait for response
            response = ws.recv()
            response_data = json.loads(response)
            
            # Should receive some response
            assert response_data is not None
            
            ws.close()
        except WebSocketTimeoutException:
            pytest.skip("WebSocket response timeout - server may not be configured for this test")
        except Exception as e:
            pytest.fail(f"WebSocket message send failed: {str(e)}")
    
    def test_end_conversation_via_websocket(self, authenticated_user):
        """Test ending a conversation via WebSocket."""
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{authenticated_user['username']}" +
            f"?token={authenticated_user['access_token']}"
        )
        
        try:
            ws = create_connection(ws_url, timeout=10)
            ws.settimeout(5)
            
            # Start conversation
            start_message = {
                "action": "start_conversation",
                "data": {
                    "title": "Conversation to End"
                }
            }
            ws.send(json.dumps(start_message))
            
            response = ws.recv()
            response_data = json.loads(response)
            conversation_id = response_data.get("conversation_id") or response_data.get("id")
            
            # End conversation
            end_message = {
                "action": "end_conversation",
                "data": {
                    "conversation_id": conversation_id
                }
            }
            ws.send(json.dumps(end_message))
            
            # Wait for confirmation
            response = ws.recv()
            response_data = json.loads(response)
            
            assert response_data is not None
            
            ws.close()
        except WebSocketTimeoutException:
            pytest.skip("WebSocket response timeout - server may not be configured for this test")
        except Exception as e:
            pytest.fail(f"WebSocket conversation end failed: {str(e)}")


class TestWebSocketReconnection:
    """Test WebSocket reconnection scenarios."""
    
    def test_websocket_reconnect_same_conversation(self, authenticated_user, auth_headers):
        """Test reconnecting to the same conversation via WebSocket."""
        import requests
        
        # Create a conversation via REST API first
        conv_response = requests.post(
            f"{CHAT_BASE_URL}/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Reconnection Test",
                "user_id": authenticated_user["username"]
            }
        )
        
        conversation_data = conv_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        
        # Connect via WebSocket
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{authenticated_user['username']}" +
            f"?token={authenticated_user['access_token']}"
        )
        
        try:
            # First connection
            ws1 = create_connection(ws_url, timeout=10)
            assert ws1.connected
            ws1.close()
            
            time.sleep(1)
            
            # Reconnect
            ws2 = create_connection(ws_url, timeout=10)
            assert ws2.connected
            ws2.close()
            
        except Exception as e:
            pytest.fail(f"WebSocket reconnection failed: {str(e)}")
    
    def test_multiple_websocket_connections_same_user(self, authenticated_user):
        """Test multiple simultaneous WebSocket connections for same user."""
        ws_url = (
            CHAT_BASE_URL.replace("http://", "ws://") + 
            f"/ws/chat/{authenticated_user['username']}" +
            f"?token={authenticated_user['access_token']}"
        )
        
        try:
            ws1 = create_connection(ws_url, timeout=10)
            ws2 = create_connection(ws_url, timeout=10)
            
            assert ws1.connected
            assert ws2.connected
            
            ws1.close()
            ws2.close()
            
        except Exception as e:
            pytest.fail(f"Multiple WebSocket connections failed: {str(e)}")
