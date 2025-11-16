"""
Quick smoke test to verify test setup is working correctly.

Run this first to ensure:
- Services are accessible
- Test dependencies are installed
- Basic connectivity works
"""
import pytest
import requests
import os

# Service URLs
AUTH_BASE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CHAT_BASE_URL = os.getenv("CHAT_SERVICE_URL", "http://localhost:8000")


def test_auth_service_is_accessible():
    """Verify auth service is running and accessible."""
    try:
        response = requests.get(f"{AUTH_BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        print(f"✓ Auth Service is accessible at {AUTH_BASE_URL}")
    except Exception as e:
        pytest.fail(f"Cannot connect to Auth Service at {AUTH_BASE_URL}: {str(e)}")


def test_chat_service_is_accessible():
    """Verify chat service is running and accessible."""
    try:
        response = requests.get(f"{CHAT_BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        print(f"✓ Chat Service is accessible at {CHAT_BASE_URL}")
    except Exception as e:
        pytest.fail(f"Cannot connect to Chat Service at {CHAT_BASE_URL}: {str(e)}")


def test_auth_service_returns_valid_health_response():
    """Verify auth service health endpoint returns expected data."""
    response = requests.get(f"{AUTH_BASE_URL}/health")
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"
    assert "service" in data
    assert data["service"] == "auth-server"
    print("✓ Auth Service health check returns valid response")


def test_chat_service_returns_valid_health_response():
    """Verify chat service health endpoint returns expected data."""
    response = requests.get(f"{CHAT_BASE_URL}/health")
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"
    print("✓ Chat Service health check returns valid response")


def test_can_access_chat_service_root():
    """Verify chat service root endpoint is accessible."""
    response = requests.get(f"{CHAT_BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "version" in data
    print("✓ Chat Service root endpoint is accessible")


if __name__ == "__main__":
    """Run smoke tests directly."""
    print("\n" + "="*50)
    print("Running Smoke Tests")
    print("="*50 + "\n")
    
    pytest.main([__file__, "-v", "-s"])
