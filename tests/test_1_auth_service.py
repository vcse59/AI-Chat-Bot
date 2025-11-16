"""
Test suite for Authentication & Authorization Service.

Tests cover:
- User registration
- User login
- Token validation
- User management (CRUD)
- Role-based access control
"""
import pytest
import requests
from conftest import AUTH_BASE_URL


class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_new_user(self, test_user_data):
        """Test successful user registration."""
        response = requests.post(
            f"{AUTH_BASE_URL}/users/",
            json={
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User created successfully"
    
    def test_register_duplicate_username(self, registered_user):
        """Test registration with duplicate username fails."""
        response = requests.post(
            f"{AUTH_BASE_URL}/users/",
            json={
                "username": registered_user["username"],
                "email": "different_email@example.com",
                "password": "AnotherPassword123!"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_register_without_roles(self, test_user_data):
        """Test that users get default 'user' role when not specified."""
        response = requests.post(
            f"{AUTH_BASE_URL}/users/",
            json={
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"]
                # No roles specified
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User created successfully"
    
    def test_register_invalid_email(self, test_user_data):
        """Test registration with invalid email format."""
        response = requests.post(
            f"{AUTH_BASE_URL}/users/",
            json={
                "username": test_user_data["username"],
                "email": "invalid-email",
                "password": test_user_data["password"]
            }
        )
        
        # Should fail validation
        assert response.status_code == 422


class TestUserAuthentication:
    """Test user authentication (login) functionality."""
    
    def test_login_success(self, registered_user):
        """Test successful login with valid credentials."""
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, registered_user):
        """Test login fails with incorrect password."""
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={
                "username": registered_user["username"],
                "password": "WrongPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    def test_login_nonexistent_user(self):
        """Test login fails with non-existent username."""
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={
                "username": "nonexistent_user_12345",
                "password": "AnyPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    def test_login_empty_password(self, registered_user):
        """Test login fails with empty password."""
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/token",
            data={
                "username": registered_user["username"],
                "password": ""
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401


class TestUserManagement:
    """Test user management endpoints (CRUD operations)."""
    
    def test_get_current_user(self, authenticated_user, auth_headers):
        """Test getting current authenticated user info."""
        response = requests.get(
            f"{AUTH_BASE_URL}/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["username"]
        assert data["email"] == authenticated_user["email"]
    
    def test_get_current_user_without_auth(self):
        """Test getting current user without authentication fails."""
        response = requests.get(f"{AUTH_BASE_URL}/users/me")
        
        assert response.status_code == 401
    
    def test_get_user_by_username_self(self, authenticated_user, auth_headers):
        """Test user can get their own data by username."""
        response = requests.get(
            f"{AUTH_BASE_URL}/users/{authenticated_user['username']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["username"]
    
    def test_update_user_email(self, authenticated_user, auth_headers):
        """Test user can update their own email."""
        new_email = f"updated_{authenticated_user['email']}"
        
        response = requests.put(
            f"{AUTH_BASE_URL}/users/{authenticated_user['username']}",
            headers=auth_headers,
            json={"email": new_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User updated successfully"
    
    def test_update_user_password(self, authenticated_user, auth_headers):
        """Test user can update their own password."""
        response = requests.put(
            f"{AUTH_BASE_URL}/users/{authenticated_user['username']}",
            headers=auth_headers,
            json={"password": "NewPassword123!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User updated successfully"


class TestRoleBasedAccessControl:
    """Test role-based access control functionality."""
    
    def test_list_users_as_admin(self, admin_headers):
        """Test admin can list all users."""
        response = requests.get(
            f"{AUTH_BASE_URL}/users/",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)
    
    def test_list_users_as_regular_user(self, auth_headers):
        """Test regular user cannot list all users."""
        response = requests.get(
            f"{AUTH_BASE_URL}/users/",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "administrator" in data["detail"].lower()
    
    def test_delete_user_as_admin(self, admin_user, admin_headers, test_user_data):
        """Test admin can delete users."""
        # Create a user to delete
        requests.post(
            f"{AUTH_BASE_URL}/users/",
            json={
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        # Delete the user as admin
        response = requests.delete(
            f"{AUTH_BASE_URL}/users/{test_user_data['username']}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User deleted successfully"
    
    def test_delete_user_as_regular_user(self, authenticated_user, auth_headers, test_user_data):
        """Test regular user cannot delete other users."""
        # Create another user
        requests.post(
            f"{AUTH_BASE_URL}/users/",
            json={
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        # Try to delete as regular user
        response = requests.delete(
            f"{AUTH_BASE_URL}/users/{test_user_data['username']}",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "administrator" in data["detail"].lower()


class TestHealthCheck:
    """Test service health check endpoint."""
    
    def test_health_endpoint(self):
        """Test health check returns healthy status."""
        response = requests.get(f"{AUTH_BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth-server"
