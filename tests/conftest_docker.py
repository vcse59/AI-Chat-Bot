"""
Docker-specific pytest configuration for MCP integration tests
Run these tests against Docker containers
"""
import pytest
import os

# Service URLs for Docker containers
AUTH_BASE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CHAT_BASE_URL = os.getenv("CHAT_SERVICE_URL", "http://localhost:8000")
TIMEZONE_MCP_URL = os.getenv("TIMEZONE_MCP_URL", "http://localhost:8003")

# Inside Docker network, services use container names
DOCKER_AUTH_URL = "http://auth-server:8001"
DOCKER_CHAT_URL = "http://openai-chatbot:8000"
DOCKER_MCP_URL = "http://timezone-mcp-server:8003"


@pytest.fixture(scope="session")
def docker_mode() -> bool:
    """Check if running in Docker mode"""
    return os.getenv("DOCKER_MODE", "false").lower() == "true"


@pytest.fixture(scope="session")
def service_urls(docker_mode: bool) -> dict:
    """Return appropriate service URLs based on mode"""
    if docker_mode:
        return {
            "auth": DOCKER_AUTH_URL,
            "chat": DOCKER_CHAT_URL,
            "mcp": DOCKER_MCP_URL
        }
    return {
        "auth": AUTH_BASE_URL,
        "chat": CHAT_BASE_URL,
        "mcp": TIMEZONE_MCP_URL
    }
