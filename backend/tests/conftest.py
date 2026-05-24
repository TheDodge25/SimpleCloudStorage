"""
Pytest configuration for integration tests.

Requires the backend to be running (either locally or via Docker).
Set BACKEND_TEST_URL env var to override the default (http://localhost:8000).

Run with: pytest tests/ -v
"""
import os
import subprocess
import uuid
import pytest
import httpx

BASE_URL = os.getenv("BACKEND_TEST_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "testadmin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "testpassword123")


@pytest.fixture(scope="session")
def unauth_client():
    """Shared synchronous HTTP client with no auth."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def check_server_and_seed_admin(unauth_client):
    """Fail fast if the backend is not reachable, and seed the admin user."""
    try:
        r = unauth_client.get("/health")
        r.raise_for_status()
    except Exception as exc:
        pytest.exit(
            f"Backend not reachable at {BASE_URL}/health — start it first.\n{exc}",
            returncode=1,
        )

    # Seed the admin user
    env = os.environ.copy()
    env["ADMIN_USERNAME"] = ADMIN_USERNAME
    env["ADMIN_PASSWORD"] = ADMIN_PASSWORD
    subprocess.run(
        ["python", "migrate_to_auth.py"],
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@pytest.fixture(scope="session")
def admin_client(unauth_client):
    """Authenticated client for the admin user."""
    c = httpx.Client(base_url=BASE_URL, timeout=30.0)
    r = c.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    r.raise_for_status()
    # The cookies are now in c.cookies
    yield c
    c.close()


@pytest.fixture
def auth_client(admin_client):
    """Authenticated client for a fresh, isolated normal user per test."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword123"
    email = f"{username}@example.com"

    r = admin_client.post("/api/v1/admin/users", json={
        "username": username,
        "email": email,
        "password": password,
        "role": "user"
    })
    r.raise_for_status()
    user_id = r.json()["id"]

    c = httpx.Client(base_url=BASE_URL, timeout=30.0)
    r_login = c.post("/api/v1/auth/login", json={"username": username, "password": password})
    r_login.raise_for_status()
    
    c.user_id = user_id  # Attach user_id for convenience
    yield c
    
    # Cleanup after test
    c.close()
    admin_client.delete(f"/api/v1/admin/users/{user_id}")
