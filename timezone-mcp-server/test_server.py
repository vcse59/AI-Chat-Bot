"""
End-to-end tests for Timezone MCP Server
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from server import (
    TimezoneMCPServer,
    AuthService,
    TimezoneService,
    UserContext,
    Settings
)


@pytest.fixture
def settings():
    """Test settings"""
    return Settings(
        AUTH_SERVICE_URL="http://localhost:8001",
        AUTH_SECRET_KEY="test-secret-key"
    )


@pytest.fixture
def timezone_service():
    """Timezone service fixture"""
    return TimezoneService()


@pytest.fixture
async def mock_auth_service():
    """Mock auth service"""
    service = AsyncMock(spec=AuthService)
    service.authenticate = AsyncMock(return_value={
        "access_token": "test_token_123",
        "token_type": "bearer"
    })
    service.verify_token = AsyncMock(return_value={
        "id": "user_001",
        "username": "testuser",
        "email": "test@example.com"
    })
    service.close = AsyncMock()
    return service


@pytest.fixture
async def mcp_server(mock_auth_service):
    """MCP server fixture with mocked auth"""
    server = TimezoneMCPServer()
    server.auth_service = mock_auth_service
    return server


class TestAuthService:
    """Test auth service integration"""
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, mock_auth_service):
        """Test successful authentication"""
        result = await mock_auth_service.authenticate("testuser", "password123")
        
        assert "access_token" in result
        assert result["access_token"] == "test_token_123"
        mock_auth_service.authenticate.assert_called_once_with("testuser", "password123")
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, mock_auth_service):
        """Test successful token verification"""
        result = await mock_auth_service.verify_token("test_token_123")
        
        assert result["username"] == "testuser"
        assert result["id"] == "user_001"
        mock_auth_service.verify_token.assert_called_once_with("test_token_123")


class TestTimezoneService:
    """Test timezone service"""
    
    def test_get_current_time(self, timezone_service):
        """Test getting current time"""
        result = timezone_service.get_current_time("America/New_York")
        
        assert result["timezone"] == "America/New_York"
        assert "current_time" in result
        assert "utc_offset" in result
        assert "timezone_abbreviation" in result
        assert "is_dst" in result
    
    def test_get_current_time_invalid_timezone(self, timezone_service):
        """Test getting current time with invalid timezone"""
        with pytest.raises(ValueError, match="Unknown timezone"):
            timezone_service.get_current_time("Invalid/Timezone")
    
    def test_list_timezones_no_filter(self, timezone_service):
        """Test listing all timezones"""
        result = timezone_service.list_timezones()
        
        assert len(result) > 0
        assert "America/New_York" in result
        assert "Europe/London" in result
    
    def test_list_timezones_with_filter(self, timezone_service):
        """Test listing timezones with filter"""
        result = timezone_service.list_timezones("America")
        
        assert len(result) > 0
        assert all("America" in tz for tz in result)
    
    def test_convert_time(self, timezone_service):
        """Test time conversion"""
        result = timezone_service.convert_time(
            "2024-01-15T12:00:00",
            "America/New_York",
            "Europe/London"
        )
        
        assert result["from_timezone"] == "America/New_York"
        assert result["to_timezone"] == "Europe/London"
        assert "converted_time" in result
        assert "utc_offset" in result
    
    @pytest.mark.asyncio
    async def test_get_timezone_by_location(self, timezone_service):
        """Test getting timezone by location"""
        result = await timezone_service.get_timezone_by_location("New York")
        assert result == "America/New_York"
        
        result = await timezone_service.get_timezone_by_location("London")
        assert result == "Europe/London"
        
        result = await timezone_service.get_timezone_by_location("Tokyo")
        assert result == "Asia/Tokyo"
    
    @pytest.mark.asyncio
    async def test_get_timezone_by_location_invalid(self, timezone_service):
        """Test getting timezone for unknown location"""
        with pytest.raises(ValueError, match="Could not determine timezone"):
            await timezone_service.get_timezone_by_location("UnknownCity")


class TestMCPServer:
    """Test MCP server functionality"""
    
    @pytest.mark.asyncio
    async def test_authenticate_handler(self, mcp_server):
        """Test authentication handler"""
        args = {
            "username": "testuser",
            "password": "password123"
        }
        
        result = await mcp_server._handle_authenticate(args)
        
        assert len(result) == 1
        assert "Authentication successful" in result[0].text
        assert "Session ID:" in result[0].text
        assert "Welcome, testuser" in result[0].text
        
        # Verify user context was created
        session_ids = [sid for sid in mcp_server.user_contexts.keys() if "testuser" in sid]
        assert len(session_ids) == 1
    
    @pytest.mark.asyncio
    async def test_authenticate_with_token_handler(self, mcp_server):
        """Test token-based authentication handler"""
        args = {
            "token": "test_oauth_token_456"
        }
        
        result = await mcp_server._handle_authenticate_with_token(args)
        
        assert len(result) == 1
        assert "Authentication successful" in result[0].text
        assert "Session ID:" in result[0].text
        assert "Welcome, testuser" in result[0].text
        
        # Verify user context was created with token
        session_ids = [sid for sid in mcp_server.user_contexts.keys() if "testuser" in sid]
        assert len(session_ids) > 0
        
        # Get the session context and verify token is stored
        session_id = list(mcp_server.user_contexts.keys())[0]
        user_context = mcp_server.user_contexts[session_id]
        assert user_context.token == "test_oauth_token_456"
    
    @pytest.mark.asyncio
    async def test_verify_session_valid_token(self, mcp_server):
        """Test session verification with valid OAuth token"""
        # Authenticate to create session
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Verify session (should validate token with auth-service)
        user_context = await mcp_server._verify_session(session_id)
        
        assert user_context.username == "testuser"
        assert user_context.token == "test_token_123"
        
        # Verify that auth service was called to validate token
        mcp_server.auth_service.verify_token.assert_called()
    
    @pytest.mark.asyncio
    async def test_verify_session_expired_token(self, mcp_server):
        """Test session verification with expired OAuth token"""
        # Authenticate to create session
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Mock token verification to fail (expired token)
        mcp_server.auth_service.verify_token = AsyncMock(side_effect=ValueError("Token expired"))
        
        # Verify session should raise error and remove context
        with pytest.raises(ValueError, match="Session expired"):
            await mcp_server._verify_session(session_id)
        
        # Verify session was removed from contexts
        assert session_id not in mcp_server.user_contexts
    
    @pytest.mark.asyncio
    async def test_tool_operation_validates_token(self, mcp_server):
        """Test that tool operations validate OAuth token on each call"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Reset mock to track calls
        mcp_server.auth_service.verify_token.reset_mock()
        
        # Perform multiple operations
        await mcp_server._handle_get_current_time({
            "session_id": session_id,
            "timezone": "UTC"
        })
        
        await mcp_server._handle_list_timezones({
            "session_id": session_id
        })
        
        await mcp_server._handle_set_default_timezone({
            "session_id": session_id,
            "timezone": "America/New_York"
        })
        
        # Verify token was validated for each operation
        assert mcp_server.auth_service.verify_token.call_count == 3
    
    @pytest.mark.asyncio
    async def test_get_current_time_with_timezone(self, mcp_server):
        """Test getting current time with explicit timezone"""
        # First authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        
        # Extract session ID
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Get current time
        args = {
            "session_id": session_id,
            "timezone": "America/New_York"
        }
        
        result = await mcp_server._handle_get_current_time(args)
        
        assert len(result) == 1
        assert "Current Time Information" in result[0].text
        assert "America/New_York" in result[0].text
        assert "User: testuser" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_current_time_with_location(self, mcp_server):
        """Test getting current time with location"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Get current time by location
        args = {
            "session_id": session_id,
            "timezone": "London"
        }
        
        result = await mcp_server._handle_get_current_time(args)
        
        assert len(result) == 1
        assert "Europe/London" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_current_time_with_default(self, mcp_server):
        """Test getting current time with default timezone"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Set default timezone
        await mcp_server._handle_set_default_timezone({
            "session_id": session_id,
            "timezone": "Asia/Tokyo"
        })
        
        # Get current time without specifying timezone
        args = {
            "session_id": session_id
        }
        
        result = await mcp_server._handle_get_current_time(args)
        
        assert len(result) == 1
        assert "Asia/Tokyo" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_current_time_invalid_session(self, mcp_server):
        """Test getting current time with invalid session"""
        args = {
            "session_id": "invalid_session",
            "timezone": "America/New_York"
        }
        
        # Should raise ValueError for invalid session
        with pytest.raises(ValueError, match="Invalid session ID"):
            await mcp_server._handle_get_current_time(args)
    
    @pytest.mark.asyncio
    async def test_list_timezones(self, mcp_server):
        """Test listing timezones"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # List timezones
        args = {
            "session_id": session_id
        }
        
        result = await mcp_server._handle_list_timezones(args)
        
        assert len(result) == 1
        assert "Available Timezones" in result[0].text
        assert "Total:" in result[0].text
        assert "User: testuser" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_timezones_filtered(self, mcp_server):
        """Test listing filtered timezones"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # List timezones with filter
        args = {
            "session_id": session_id,
            "filter": "America"
        }
        
        result = await mcp_server._handle_list_timezones(args)
        
        assert len(result) == 1
        assert "filtered by 'America'" in result[0].text
        assert "America" in result[0].text
    
    @pytest.mark.asyncio
    async def test_convert_time(self, mcp_server):
        """Test time conversion"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Convert time
        args = {
            "session_id": session_id,
            "time": "2024-01-15T12:00:00",
            "from_timezone": "America/New_York",
            "to_timezone": "Europe/London"
        }
        
        result = await mcp_server._handle_convert_time(args)
        
        assert len(result) == 1
        assert "Time Conversion" in result[0].text
        assert "America/New_York" in result[0].text
        assert "Europe/London" in result[0].text
        assert "User: testuser" in result[0].text
    
    @pytest.mark.asyncio
    async def test_set_default_timezone(self, mcp_server):
        """Test setting default timezone"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Set default timezone
        args = {
            "session_id": session_id,
            "timezone": "America/Los_Angeles"
        }
        
        result = await mcp_server._handle_set_default_timezone(args)
        
        assert len(result) == 1
        assert "Default Timezone Updated" in result[0].text
        assert "America/Los_Angeles" in result[0].text
        
        # Verify context was updated
        user_context = mcp_server.user_contexts[session_id]
        assert user_context.default_timezone == "America/Los_Angeles"
    
    @pytest.mark.asyncio
    async def test_set_default_timezone_by_location(self, mcp_server):
        """Test setting default timezone by location"""
        # Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Set default timezone by location
        args = {
            "session_id": session_id,
            "timezone": "Paris"
        }
        
        result = await mcp_server._handle_set_default_timezone(args)
        
        assert len(result) == 1
        assert "Europe/Paris" in result[0].text
        
        # Verify context
        user_context = mcp_server.user_contexts[session_id]
        assert user_context.default_timezone == "Europe/Paris"


class TestEndToEndFlow:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_user_flow(self, mcp_server):
        """Test complete user flow from authentication to timezone operations"""
        
        # Step 1: Authenticate
        auth_result = await mcp_server._handle_authenticate({
            "username": "testuser",
            "password": "password123"
        })
        
        assert "Authentication successful" in auth_result[0].text
        session_id = auth_result[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Step 2: Set default timezone
        set_default_result = await mcp_server._handle_set_default_timezone({
            "session_id": session_id,
            "timezone": "New York"
        })
        
        assert "Default Timezone Updated" in set_default_result[0].text
        assert "America/New_York" in set_default_result[0].text
        
        # Step 3: Get current time (should use default)
        current_time_result = await mcp_server._handle_get_current_time({
            "session_id": session_id
        })
        
        assert "America/New_York" in current_time_result[0].text
        assert "User: testuser" in current_time_result[0].text
        
        # Step 4: List timezones
        list_result = await mcp_server._handle_list_timezones({
            "session_id": session_id,
            "filter": "Asia"
        })
        
        assert "filtered by 'Asia'" in list_result[0].text
        
        # Step 5: Convert time
        convert_result = await mcp_server._handle_convert_time({
            "session_id": session_id,
            "time": "2024-01-15T14:30:00",
            "from_timezone": "America/New_York",
            "to_timezone": "Asia/Tokyo"
        })
        
        assert "Time Conversion" in convert_result[0].text
        assert "User: testuser" in convert_result[0].text
        
        # Step 6: Get current time in different timezone
        other_tz_result = await mcp_server._handle_get_current_time({
            "session_id": session_id,
            "timezone": "London"
        })
        
        assert "Europe/London" in other_tz_result[0].text
    
    @pytest.mark.asyncio
    async def test_multiple_users_context_isolation(self, mcp_server):
        """Test that multiple users have isolated contexts"""
        
        # Authenticate user 1
        auth1 = await mcp_server._handle_authenticate({
            "username": "user1",
            "password": "pass1"
        })
        session1 = auth1[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Authenticate user 2
        mcp_server.auth_service.verify_token = AsyncMock(return_value={
            "id": "user_002",
            "username": "user2",
            "email": "user2@example.com"
        })
        
        auth2 = await mcp_server._handle_authenticate({
            "username": "user2",
            "password": "pass2"
        })
        session2 = auth2[0].text.split("Session ID: ")[1].split("\n")[0]
        
        # Set different default timezones
        await mcp_server._handle_set_default_timezone({
            "session_id": session1,
            "timezone": "America/New_York"
        })
        
        await mcp_server._handle_set_default_timezone({
            "session_id": session2,
            "timezone": "Asia/Tokyo"
        })
        
        # Verify contexts are isolated
        ctx1 = mcp_server.user_contexts[session1]
        ctx2 = mcp_server.user_contexts[session2]
        
        assert ctx1.username == "user1"
        assert ctx2.username == "user2"
        assert ctx1.default_timezone == "America/New_York"
        assert ctx2.default_timezone == "Asia/Tokyo"
        
        # Get current time for each user
        result1 = await mcp_server._handle_get_current_time({"session_id": session1})
        result2 = await mcp_server._handle_get_current_time({"session_id": session2})
        
        assert "America/New_York" in result1[0].text
        assert "User: user1" in result1[0].text
        assert "Asia/Tokyo" in result2[0].text
        assert "User: user2" in result2[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
