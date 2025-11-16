
from fastapi.testclient import TestClient
from auth_server.main import app
from auth_server.database import get_db
from .test_main import override_get_db, setup_database

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"username": "testuser2", "email": "testuser2@example.com", "password": "testpassword", "roles": ["user"]})
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_create_user_existing_username():
    client.post("/users/", json={"username": "testuser3", "email": "testuser3@example.com", "password": "testpassword", "roles": ["user"]})
    response = client.post("/users/", json={"username": "testuser3", "email": "testuser3@example.com", "password": "testpassword", "roles": ["user"]})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_list_users_as_admin():
    # Create an admin user
    client.post("/users/", json={"username": "adminuser", "email": "adminuser@example.com", "password": "adminpassword", "roles": ["admin"]})
    # Get a token for the admin user
    response = client.post("/auth/token", data={"username": "adminuser", "password": "adminpassword"})
    token = response.json()["access_token"]
    # List users
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "users" in response.json()

def test_list_users_as_non_admin():
    # Create a non-admin user
    client.post("/users/", json={"username": "nonadmin", "email": "nonadmin@example.com", "password": "password", "roles": ["user"]})
    # Get a token for the non-admin user
    response = client.post("/auth/token", data={"username": "nonadmin", "password": "password"})
    token = response.json()["access_token"]
    # Try to list users
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Only administrators can list all users"

def test_read_users_me():
    # Create a user
    client.post("/users/", json={"username": "me_user", "email": "me_user@example.com", "password": "password", "roles": ["user"]})
    # Get a token
    response = client.post("/auth/token", data={"username": "me_user", "password": "password"})
    token = response.json()["access_token"]
    # Get user's own data
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "me_user"

def test_read_user_as_admin():
    # Create an admin and a target user
    client.post("/users/", json={"username": "admin_read", "email": "admin_read@example.com", "password": "password", "roles": ["admin"]})
    client.post("/users/", json={"username": "target_user", "email": "target_user@example.com", "password": "password", "roles": ["user"]})
    # Get admin token
    response = client.post("/auth/token", data={"username": "admin_read", "password": "password"})
    token = response.json()["access_token"]
    # Admin reads target user's data
    response = client.get("/users/target_user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "target_user"

def test_read_user_as_self():
    # Create a user
    client.post("/users/", json={"username": "self_user", "email": "self_user@example.com", "password": "password", "roles": ["user"]})
    # Get token
    response = client.post("/auth/token", data={"username": "self_user", "password": "password"})
    token = response.json()["access_token"]
    # User reads their own data
    response = client.get("/users/self_user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "self_user"

def test_read_user_unauthorized():
    # Create two users
    client.post("/users/", json={"username": "user1_unauth", "email": "user1_unauth@example.com", "password": "password", "roles": ["user"]})
    client.post("/users/", json={"username": "user2_unauth", "email": "user2_unauth@example.com", "password": "password", "roles": ["user"]})
    # Get token for user1
    response = client.post("/auth/token", data={"username": "user1_unauth", "password": "password"})
    token = response.json()["access_token"]
    # user1 tries to read user2's data
    response = client.get("/users/user2_unauth", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"

def test_update_user_as_admin():
    # Create admin and target user
    client.post("/users/", json={"username": "admin_update", "email": "admin_update@example.com", "password": "password", "roles": ["admin"]})
    client.post("/users/", json={"username": "target_update", "email": "target_update@example.com", "password": "password", "roles": ["user"]})
    # Get admin token
    response = client.post("/auth/token", data={"username": "admin_update", "password": "password"})
    token = response.json()["access_token"]
    # Admin updates target user
    response = client.put("/users/target_update", headers={"Authorization": f"Bearer {token}"}, json={"email": "newemail@example.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "User updated successfully"

def test_update_user_as_self():
    # Create user
    client.post("/users/", json={"username": "self_update", "email": "self_update@example.com", "password": "password", "roles": ["user"]})
    # Get token
    response = client.post("/auth/token", data={"username": "self_update", "password": "password"})
    token = response.json()["access_token"]
    # User updates their own data
    response = client.put("/users/self_update", headers={"Authorization": f"Bearer {token}"}, json={"email": "new_self_email@example.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "User updated successfully"

def test_delete_user_as_admin():
    # Create admin and target user
    client.post("/users/", json={"username": "admin_delete", "email": "admin_delete@example.com", "password": "password", "roles": ["admin"]})
    client.post("/users/", json={"username": "target_delete", "email": "target_delete@example.com", "password": "password", "roles": ["user"]})
    # Get admin token
    response = client.post("/auth/token", data={"username": "admin_delete", "password": "password"})
    token = response.json()["access_token"]
    # Admin deletes target user
    response = client.delete("/users/target_delete", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

def test_delete_user_as_non_admin():
    # Create two users
    client.post("/users/", json={"username": "user1_delete", "email": "user1_delete@example.com", "password": "password", "roles": ["user"]})
    client.post("/users/", json={"username": "user2_delete", "email": "user2_delete@example.com", "password": "password", "roles": ["user"]})
    # Get token for user1
    response = client.post("/auth/token", data={"username": "user1_delete", "password": "password"})
    token = response.json()["access_token"]
    # user1 tries to delete user2
    response = client.delete("/users/user2_delete", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Only administrators can delete users"
