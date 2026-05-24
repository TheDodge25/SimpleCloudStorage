"""Integration tests for /api/v1/admin endpoints."""
import uuid

def test_admin_can_list_users(admin_client):
    r = admin_client.get("/api/v1/admin/users")
    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    assert "hashed_password" not in users[0]


def test_normal_user_is_forbidden_from_admin_endpoints(auth_client):
    r = auth_client.get("/api/v1/admin/users")
    assert r.status_code == 403


def test_admin_can_create_and_delete_user(admin_client):
    username = f"new_admin_target_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"
    
    # Create
    r = admin_client.post("/api/v1/admin/users", json={
        "username": username,
        "email": email,
        "password": "strongpassword123",
        "role": "user"
    })
    assert r.status_code == 201
    user_id = r.json()["id"]
    
    # Verify in list
    r_list = admin_client.get("/api/v1/admin/users")
    assert any(u["id"] == user_id for u in r_list.json())
    
    # Delete
    r_del = admin_client.delete(f"/api/v1/admin/users/{user_id}")
    assert r_del.status_code == 204
    
    # Verify gone
    r_list2 = admin_client.get("/api/v1/admin/users")
    assert not any(u["id"] == user_id for u in r_list2.json())


def test_admin_can_update_user_quota_and_role(admin_client):
    # Setup test user
    username = f"update_target_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"
    r_create = admin_client.post("/api/v1/admin/users", json={
        "username": username,
        "email": email,
        "password": "strongpassword123",
        "role": "user"
    })
    user_id = r_create.json()["id"]
    
    # Update quota and role
    r_patch = admin_client.patch(f"/api/v1/admin/users/{user_id}", json={
        "role": "admin",
        "quota_bytes": 5000000000
    })
    assert r_patch.status_code == 200
    data = r_patch.json()
    assert data["role"] == "admin"
    assert data["quota_bytes"] == 5000000000
    
    # Cleanup
    admin_client.delete(f"/api/v1/admin/users/{user_id}")
