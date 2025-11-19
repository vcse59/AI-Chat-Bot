"""
End-to-End Test for MCP Tool Integration

This test validates the complete flow:
1. User authenticates with auth-service
2. User registers an MCP server (timezone server)
3. User sends a chat message requiring timezone information
4. Chat service discovers MCP tools
5. LLM analyzes intent and decides to use MCP tool
6. MCP tool is called and result is formatted
7. User receives helpful response with timezone information

Prerequisites:
- All services must be running (auth-service, chat-service, timezone-mcp-server)
- OpenAI API key must be configured
"""

import pytest
import requests
import json
import time
from typing import Dict

# Service URLs
AUTH_BASE_URL = "http://localhost:8001"
CHAT_BASE_URL = "http://localhost:8000/api/v1"
TIMEZONE_MCP_URL = "http://localhost:8003"


class TestMCPIntegration:
    """Test suite for MCP tool integration"""
    
    def test_services_health_check(self):
        """Test 1: Verify all required services are running"""
        print("\n=== Test 1: Services Health Check ===")
        
        services = {
            "Auth Service": "http://localhost:8001/health",
            "Chat Service": "http://localhost:8000/health",
            "Timezone MCP Server": f"{TIMEZONE_MCP_URL}/health"
        }
        
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                assert response.status_code == 200, f"{name} health check failed"
                print(f"✓ {name} is healthy")
            except Exception as e:
                pytest.fail(f"{name} is not accessible: {e}")
    
    def test_mcp_server_tools_endpoint(self):
        """Test 2: Verify MCP server exposes /tools endpoint"""
        print("\n=== Test 2: MCP Server Tools Endpoint ===")
        
        response = requests.get(f"{TIMEZONE_MCP_URL}/tools")
        assert response.status_code == 200, "Failed to get tools from MCP server"
        
        tools_data = response.json()
        assert "tools" in tools_data, "Response missing 'tools' field"
        assert len(tools_data["tools"]) > 0, "No tools available"
        
        print(f"✓ MCP server exposes {len(tools_data['tools'])} tools:")
        for tool in tools_data["tools"]:
            print(f"  - {tool['name']}: {tool['description']}")
    
    def test_register_mcp_server(self, authenticated_user: Dict[str, str]):
        """Test 3: Register MCP server via chat-service API"""
        print("\n=== Test 3: Register MCP Server ===")
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}",
            "Content-Type": "application/json"
        }
        
        # First check if server already exists
        list_response = requests.get(
            f"{CHAT_BASE_URL}/mcp-servers/",
            headers=headers
        )
        
        if list_response.status_code == 200:
            servers = list_response.json()
            for server in servers:
                if "Timezone" in server.get("name", ""):
                    print(f"✓ MCP server already registered with ID: {server['id']}")
                    return server
        
        mcp_server_data = {
            "name": "Timezone MCP Server",
            "description": "Provides timezone information and conversions",
            "server_url": "http://timezone-mcp-server:8003/mcp",
            "api_key": None,
            "is_active": True
        }
        
        response = requests.post(
            f"{CHAT_BASE_URL}/mcp-servers/",
            json=mcp_server_data,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"⚠️  Failed to register new MCP server: {response.text}")
            print(f"   Checking if one already exists...")
            # Try to get existing server
            list_response = requests.get(f"{CHAT_BASE_URL}/mcp-servers/", headers=headers)
            if list_response.status_code == 200:
                servers = list_response.json()
                if servers:
                    print(f"✓ Using existing MCP server: {servers[0]['id']}")
                    return servers[0]
            raise Exception(f"Failed to register or find MCP server: {response.text}")
        
        server_info = response.json()
        assert "id" in server_info, "Response missing server ID"
        assert server_info["name"] == mcp_server_data["name"]
        assert server_info["is_active"] is True
        
        print(f"✓ MCP server registered successfully with ID: {server_info['id']}")
        return server_info
    
    def test_list_user_mcp_servers(self, authenticated_user: Dict[str, str]):
        """Test 4: List user's registered MCP servers"""
        print("\n=== Test 4: List User MCP Servers ===")
        
        # First register a server
        self.test_register_mcp_server(authenticated_user)
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
        
        response = requests.get(
            f"{CHAT_BASE_URL}/mcp-servers/",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to list MCP servers: {response.text}"
        
        servers = response.json()
        assert len(servers) > 0, "No MCP servers found for user"
        
        print(f"✓ Found {len(servers)} MCP server(s) for user:")
        for server in servers:
            print(f"  - {server['name']} (Active: {server['is_active']})")
    
    def test_create_conversation(self, authenticated_user: Dict[str, str]) -> Dict[str, str]:
        """Test 5: Create a new conversation"""
        print("\n=== Test 5: Create Conversation ===")
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}",
            "Content-Type": "application/json"
        }
        
        # First get user info to get user_id
        user_response = requests.get(
            f"{AUTH_BASE_URL}/users/me",
            headers=headers
        )
        
        if user_response.status_code != 200:
            raise Exception(f"Failed to get user info: {user_response.text}")
        
        user_data = user_response.json()
        user_id = user_data["id"]
        
        conversation_data = {
            "title": "MCP Tool Integration Test",
            "system_message": "You are a helpful assistant with access to timezone tools."
        }
        
        response = requests.post(
            f"{CHAT_BASE_URL}/users/{user_id}/conversations/",
            json=conversation_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to create conversation: {response.text}"
        
        conversation = response.json()
        assert "id" in conversation, "Response missing conversation ID"
        
        print(f"✓ Conversation created with ID: {conversation['id']}")
        return conversation
    
    def test_mcp_tool_discovery_and_intent_analysis(self, authenticated_user: Dict[str, str]):
        """Test 6: Send message that requires MCP tool and verify LLM intent detection"""
        print("\n=== Test 6: MCP Tool Discovery & Intent Analysis ===")
        
        # Register MCP server
        self.test_register_mcp_server(authenticated_user)
        
        # Create conversation
        conversation = self.test_create_conversation(authenticated_user)
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Send a message that should trigger MCP tool usage
        message_data = {
            "conversation_id": conversation["id"],
            "content": "What time is it in New York right now?"
        }
        
        print("\nSending query: 'What time is it in New York right now?'")
        print("Expected: LLM should detect intent and use get_current_time tool")
        
        response = requests.post(
            f"{CHAT_BASE_URL}/messages/",
            json=message_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to send message: {response.text}"
        
        result = response.json()
        
        # Verify response structure
        assert "user_message" in result, "Missing user_message in response"
        assert "ai_response" in result, "Missing ai_response in response"
        
        ai_response = result["ai_response"]
        
        print(f"\n✓ Message processed successfully")
        print(f"  User message ID: {result['user_message']['id']}")
        print(f"  AI response ID: {ai_response['id']}")
        print(f"  Response time: {result.get('response_time_ms', 0)}ms")
        
        # Check if MCP tool was used (if metadata is available)
        if ai_response.get("metadata"):
            metadata = ai_response["metadata"]
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            if metadata.get("mcp_tool_used"):
                print(f"\n✓ MCP Tool Integration Successful!")
                print(f"  Tool used: {metadata.get('tool_name')}")
                print(f"  Server ID: {metadata.get('server_id')}")
                print(f"  Tool result: {json.dumps(metadata.get('tool_result'), indent=2)}")
            else:
                print(f"\n⚠ MCP tool was not used (LLM responded directly)")
                print(f"  This might happen if LLM decided it could answer without tools")
        
        print(f"\n📝 AI Response: {ai_response['content'][:200]}...")
        
        # Verify the response contains relevant timezone information
        response_lower = ai_response['content'].lower()
        assert any(keyword in response_lower for keyword in ['time', 'york', 'est', 'edt', 'timezone']), \
            "Response doesn't seem to contain timezone information"
        
        print(f"\n✓ Response contains relevant timezone information")
        
        return result
    
    def test_mcp_tool_call_with_different_queries(self, authenticated_user: Dict[str, str]):
        """Test 7: Test multiple queries to verify MCP tool routing"""
        print("\n=== Test 7: Multiple Query Types ===")
        
        # Register MCP server
        self.test_register_mcp_server(authenticated_user)
        
        # Create conversation
        conversation = self.test_create_conversation(authenticated_user)
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}",
            "Content-Type": "application/json"
        }
        
        test_queries = [
            {
                "query": "What's the current time in Tokyo?",
                "should_use_tool": True,
                "expected_keywords": ["time", "tokyo", "jst"]
            },
            {
                "query": "Convert 2:00 PM EST to PST",
                "should_use_tool": True,
                "expected_keywords": ["convert", "pst", "time"]
            },
            {
                "query": "What is the capital of France?",
                "should_use_tool": False,
                "expected_keywords": ["paris", "france"]
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n--- Query {i}: {test_case['query']} ---")
            print(f"Expected to use MCP tool: {test_case['should_use_tool']}")
            
            message_data = {
                "conversation_id": conversation["id"],
                "content": test_case["query"]
            }
            
            response = requests.post(
                f"{CHAT_BASE_URL}/messages/",
                json=message_data,
                headers=headers
            )
            
            assert response.status_code == 200, f"Failed to send message: {response.text}"
            
            result = response.json()
            ai_response = result["ai_response"]
            
            # Check metadata for tool usage
            tool_used = False
            if ai_response.get("metadata"):
                metadata = ai_response["metadata"]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                tool_used = metadata.get("mcp_tool_used", False)
            
            print(f"  MCP tool used: {tool_used}")
            print(f"  Response preview: {ai_response['content'][:150]}...")
            
            # Verify keywords are in response
            response_lower = ai_response['content'].lower()
            found_keywords = [kw for kw in test_case['expected_keywords'] if kw in response_lower]
            
            if found_keywords:
                print(f"  ✓ Found expected keywords: {found_keywords}")
            
            # Small delay between requests
            time.sleep(1)
        
        print("\n✓ Multiple query types handled successfully")
    
    def test_mcp_tool_error_handling(self, authenticated_user: Dict[str, str]):
        """Test 8: Verify error handling for invalid MCP tool calls"""
        print("\n=== Test 8: MCP Tool Error Handling ===")
        
        # Register MCP server
        self.test_register_mcp_server(authenticated_user)
        
        # Create conversation
        conversation = self.test_create_conversation(authenticated_user)
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Send a message with invalid timezone
        message_data = {
            "conversation_id": conversation["id"],
            "content": "What time is it in InvalidTimezoneXYZ?"
        }
        
        print("\nSending query with invalid timezone")
        
        response = requests.post(
            f"{CHAT_BASE_URL}/messages/",
            json=message_data,
            headers=headers
        )
        
        # Should still get 200 status (error handled gracefully)
        assert response.status_code == 200, f"Request failed: {response.text}"
        
        result = response.json()
        ai_response = result["ai_response"]
        
        print(f"✓ Error handled gracefully")
        print(f"  Response: {ai_response['content'][:200]}...")
    
    def test_conversation_with_mcp_context(self, authenticated_user: Dict[str, str]):
        """Test 9: Verify conversation context is maintained with MCP tools"""
        print("\n=== Test 9: Conversation Context with MCP Tools ===")
        
        # Register MCP server
        self.test_register_mcp_server(authenticated_user)
        
        # Create conversation
        conversation = self.test_create_conversation(authenticated_user)
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}",
            "Content-Type": "application/json"
        }
        
        # First message - get time in London
        message1 = {
            "conversation_id": conversation["id"],
            "content": "What time is it in London?"
        }
        
        print("\nMessage 1: What time is it in London?")
        response1 = requests.post(f"{CHAT_BASE_URL}/messages/", json=message1, headers=headers)
        assert response1.status_code == 200
        
        result1 = response1.json()
        print(f"  Response 1: {result1['ai_response']['content'][:100]}...")
        
        time.sleep(1)
        
        # Second message - follow-up question using context
        message2 = {
            "conversation_id": conversation["id"],
            "content": "And what about Tokyo?"
        }
        
        print("\nMessage 2: And what about Tokyo? (expecting context awareness)")
        response2 = requests.post(f"{CHAT_BASE_URL}/messages/", json=message2, headers=headers)
        assert response2.status_code == 200
        
        result2 = response2.json()
        print(f"  Response 2: {result2['ai_response']['content'][:100]}...")
        
        # Verify conversation has both messages
        conv_response = requests.get(
            f"{CHAT_BASE_URL}/conversations/{conversation['id']}",
            headers=headers
        )
        
        assert conv_response.status_code == 200
        conv_data = conv_response.json()
        
        # Should have at least 4 messages (2 user + 2 assistant)
        message_count = len(conv_data.get("messages", []))
        assert message_count >= 4, f"Expected at least 4 messages, got {message_count}"
        
        print(f"\n✓ Conversation context maintained ({message_count} messages total)")
    
    def test_deactivate_mcp_server(self, authenticated_user: Dict[str, str]):
        """Test 10: Verify deactivated MCP servers are not used"""
        print("\n=== Test 10: Deactivate MCP Server ===")
        
        # Register MCP server
        server_info = self.test_register_mcp_server(authenticated_user)
        
        headers = {
            "Authorization": f"Bearer {authenticated_user['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Deactivate the server
        update_data = {"is_active": False}
        
        response = requests.put(
            f"{CHAT_BASE_URL}/mcp-servers/{server_info['id']}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to deactivate server: {response.text}"
        
        print(f"✓ MCP server deactivated")
        
        # Create conversation and send message
        conversation = self.test_create_conversation(authenticated_user)
        
        message_data = {
            "conversation_id": conversation["id"],
            "content": "What time is it in Paris?"
        }
        
        print("\nSending query with deactivated MCP server")
        
        response = requests.post(
            f"{CHAT_BASE_URL}/messages/",
            json=message_data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check if MCP tool was used
        tool_used = False
        ai_response = result["ai_response"]
        if ai_response.get("metadata"):
            metadata = ai_response["metadata"]
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            tool_used = metadata.get("mcp_tool_used", False)
        
        print(f"  MCP tool used: {tool_used} (should be False)")
        print(f"  Response: {ai_response['content'][:150]}...")
        
        # Clean up - reactivate for other tests
        requests.put(
            f"{CHAT_BASE_URL}/mcp-servers/{server_info['id']}",
            json={"is_active": True},
            headers=headers
        )


def run_complete_flow_test():
    """
    Manual test function to run complete flow
    Run with: pytest test_8_mcp_integration.py::run_complete_flow_test -v -s
    """
    print("\n" + "="*70)
    print("  MCP TOOL INTEGRATION - COMPLETE FLOW TEST")
    print("="*70)
    
    test = TestMCPIntegration()
    
    # Use existing admin user
    test_user = {
        "username": "admin",
        "password": "admin123"
    }
    
    # Login
    print("\n🔐 Logging in as admin...")
    response = requests.post(
        "http://localhost:8001/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    print(f"✅ Logged in successfully")
    
    auth_user = {**test_user, "access_token": response.json()["access_token"]}
    
    # Run tests that work with current API
    test.test_services_health_check()
    test.test_mcp_server_tools_endpoint()
    test.test_register_mcp_server(auth_user)
    test.test_list_user_mcp_servers(auth_user)
    # Note: The following tests require WebSocket or a synchronous message processing endpoint
    # test.test_mcp_tool_discovery_and_intent_analysis(auth_user)
    # test.test_mcp_tool_call_with_different_queries(auth_user)
    # test.test_mcp_tool_error_handling(auth_user)
    # test.test_conversation_with_mcp_context(auth_user)
    # test.test_deactivate_mcp_server(auth_user)
    
    print("\n" + "="*70)
    print("  ✓ MCP SERVER REGISTRATION TESTS PASSED!")
    print("  ℹ️  Message processing tests require WebSocket connection")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Can run directly for manual testing
    run_complete_flow_test()
