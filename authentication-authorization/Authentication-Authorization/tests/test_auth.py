
from fastapi.testclient import TestClient
from auth_server.main import app
from auth_server.database import get_db
from .test_main import override_get_db
import time
from jose import jwt
from auth_server.security import SECRET_KEY, ALGORITHM

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_login_for_access_token():
    # Create a user to test login
    client.post("/users/", json={"username": "testuser", "email": "testuser@example.com", "password": "testpassword", "roles": ["user"]})

    # Test successful login
    response = client.post("/auth/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Test unsuccessful login
    response = client.post("/auth/token", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

    # Test login with non-existent user
    response = client.post("/auth/token", data={"username": "nonexistentuser", "password": "testpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

    # Test login with empty password
    response = client.post("/auth/token", data={"username": "testuser", "password": ""})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_expired_token():
    # Create a user
    client.post("/users/", json={"username": "exp_user", "email": "exp_user@example.com", "password": "password", "roles": ["user"]})
    
    # Manually create an expired token
    from datetime import timedelta
    from auth_server.security.auth import create_access_token
    
    # Create a token that expires in 1 second
    token = create_access_token(
        data={"sub": "exp_user", "roles": ["user"]},
        expires_delta=timedelta(seconds=1)
    )
    
    # Wait for the token to expire
    time.sleep(2)
    
    # Try to access a protected route
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
