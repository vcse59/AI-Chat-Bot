
from fastapi.testclient import TestClient
from auth_server.main import app
from auth_server.database import get_db
from .test_main import override_get_db, setup_database

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_update_user_roles_as_admin():
    # Create admin and target user
    client.post("/users/", json={"username": "admin_roles", "email": "admin_roles@example.com", "password": "password", "roles": ["admin"]})
    client.post("/users/", json={"username": "target_roles", "email": "target_roles@example.com", "password": "password", "roles": ["user"]})
    # Get admin token
    response = client.post("/auth/token", data={"username": "admin_roles", "password": "password"})
    token = response.json()["access_token"]
    # Admin updates target user's roles
    response = client.put("/roles/target_roles", headers={"Authorization": f"Bearer {token}"}, json={"roles": ["manager"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Roles updated successfully for user target_roles"

def test_update_user_roles_as_non_admin():
    # Create two users
    client.post("/users/", json={"username": "user1_roles", "email": "user1_roles@example.com", "password": "password", "roles": ["user"]})
    client.post("/users/", json={"username": "user2_roles", "email": "user2_roles@example.com", "password": "password", "roles": ["user"]})
    # Get token for user1
    response = client.post("/auth/token", data={"username": "user1_roles", "password": "password"})
    token = response.json()["access_token"]
    # user1 tries to update user2's roles
    response = client.put("/roles/user2_roles", headers={"Authorization": f"Bearer {token}"}, json={"roles": ["manager"]})
    assert response.status_code == 403
    assert response.json()["detail"] == "Only administrators can update user roles"

def test_update_user_roles_with_nonexistent_role():
    # Create admin and target user
    client.post("/users/", json={"username": "admin_roles_nonexistent", "email": "admin_roles_nonexistent@example.com", "password": "password", "roles": ["admin"]})
    client.post("/users/", json={"username": "target_roles_nonexistent", "email": "target_roles_nonexistent@example.com", "password": "password", "roles": ["user"]})
    # Get admin token
    response = client.post("/auth/token", data={"username": "admin_roles_nonexistent", "password": "password"})
    token = response.json()["access_token"]
    # Admin tries to update target user's roles with a nonexistent role
    response = client.put("/roles/target_roles_nonexistent", headers={"Authorization": f"Bearer {token}"}, json={"roles": ["nonexistent_role"]})
    assert response.status_code == 400
    assert response.json()["detail"] == "Role 'nonexistent_role' does not exist"
