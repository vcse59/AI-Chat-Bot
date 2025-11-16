"""
Pytest configuration and fixtures for end-to-end tests.
"""
import pytest
import os
import time
import requests
from typing import Dict, Generator

# Service URLs
AUTH_BASE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CHAT_BASE_URL = os.getenv("CHAT_SERVICE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@pytest.fixture(scope="session", autouse=True)
def wait_for_services():
    """Wait for all services to be ready before running tests."""
    services = {
        "auth-server": f"{AUTH_BASE_URL}/health",
        "chat-api": f"{CHAT_BASE_URL}/health",
    }
    
    max_retries = 30
    retry_delay = 2
    
    for service_name, health_url in services.items():
        print(f"\nWaiting for {service_name} to be ready...")
        for i in range(max_retries):
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print(f"✓ {service_name} is ready")
                    break
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"{service_name} did not become ready in time")


@pytest.fixture(scope="function")
def test_user_data() -> Dict[str, str]:
    """Generate unique test user data for each test."""
    timestamp = int(time.time() * 1000)
    return {
        "username": f"testuser_{timestamp}",
        "email": f"testuser_{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": f"Test User {timestamp}"
    }


@pytest.fixture(scope="function")
def registered_user(test_user_data: Dict[str, str]) -> Dict[str, str]:
    """Create and return a registered user."""
    # Register the user
    response = requests.post(
        f"{AUTH_BASE_URL}/users/",
        json={
            "username": test_user_data["username"],
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200, f"Failed to register user: {response.text}"
    
    return test_user_data


@pytest.fixture(scope="function")
def authenticated_user(registered_user: Dict[str, str]) -> Dict[str, str]:
    """Create a registered user and return authentication token."""
    # Login to get token
    response = requests.post(
        f"{AUTH_BASE_URL}/auth/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    
    token_data = response.json()
    return {
        **registered_user,
        "access_token": token_data["access_token"],
        "token_type": token_data["token_type"]
    }


@pytest.fixture(scope="function")
def admin_user() -> Dict[str, str]:
    """Create and return an admin user with authentication token."""
    timestamp = int(time.time() * 1000)
    admin_data = {
        "username": f"admin_{timestamp}",
        "email": f"admin_{timestamp}@example.com",
        "password": "AdminPassword123!",
    }
    
    # Register admin user
    response = requests.post(
        f"{AUTH_BASE_URL}/users/",
        json={
            "username": admin_data["username"],
            "email": admin_data["email"],
            "password": admin_data["password"],
            "roles": ["admin", "user"]
        }
    )
    assert response.status_code == 200, f"Failed to register admin: {response.text}"
    
    # Login to get token
    response = requests.post(
        f"{AUTH_BASE_URL}/auth/token",
        data={
            "username": admin_data["username"],
            "password": admin_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200, f"Failed to login admin: {response.text}"
    
    token_data = response.json()
    return {
        **admin_data,
        "access_token": token_data["access_token"],
        "token_type": token_data["token_type"]
    }


@pytest.fixture(scope="function")
def auth_headers(authenticated_user: Dict[str, str]) -> Dict[str, str]:
    """Return authorization headers for authenticated requests."""
    return {
        "Authorization": f"Bearer {authenticated_user['access_token']}"
    }


@pytest.fixture(scope="function")
def admin_headers(admin_user: Dict[str, str]) -> Dict[str, str]:
    """Return authorization headers for admin requests."""
    return {
        "Authorization": f"Bearer {admin_user['access_token']}"
    }
