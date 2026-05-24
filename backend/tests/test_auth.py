"""Integration tests for /api/v1/auth endpoints."""
import uuid

def test_login_success_sets_cookies(admin_client, unauth_client):
    # Use unauth_client to login manually so we can inspect cookies
    from tests.conftest import ADMIN_USERNAME, ADMIN_PASSWORD
    r = unauth_client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert r.status_code == 200
    assert "access_token" in r.cookies
    assert "refresh_token" in r.cookies
    
    # HttpOnly cookies shouldn't be exposed in json, but the user info should be
    data = r.json()
    assert "user" in data
    assert data["user"]["username"] == ADMIN_USERNAME


def test_login_failure_invalid_credentials(unauth_client):
    r = unauth_client.post("/api/v1/auth/login", json={"username": "wrong", "password": "wrong"})
    assert r.status_code == 401


def test_refresh_token_rotates_credentials(admin_client, unauth_client):
    from tests.conftest import ADMIN_USERNAME, ADMIN_PASSWORD
    # 1. Login
    r_login = unauth_client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert r_login.status_code == 200
    access1 = r_login.cookies.get("access_token")
    refresh1 = r_login.cookies.get("refresh_token")
    
    # 2. Refresh
    r_refresh = unauth_client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh1})
    assert r_refresh.status_code == 200
    access2 = r_refresh.cookies.get("access_token")
    refresh2 = r_refresh.cookies.get("refresh_token")
    
    assert access1 != access2
    assert refresh1 != refresh2

    # 3. Old refresh token should now be revoked
    r_refresh_fail = unauth_client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh1})
    assert r_refresh_fail.status_code == 401


def test_logout_clears_cookies(unauth_client):
    from tests.conftest import ADMIN_USERNAME, ADMIN_PASSWORD
    unauth_client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    
    r_logout = unauth_client.post("/api/v1/auth/logout")
    # Actually wait, test client handles cookies automatically, let's see if they are cleared.
    assert "access_token" not in unauth_client.cookies or unauth_client.cookies.get("access_token") == '""' or not unauth_client.cookies.get("access_token")


def test_me_returns_user_profile(auth_client):
    r = auth_client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert "username" in r.json()
    assert "quota_bytes" in r.json()
