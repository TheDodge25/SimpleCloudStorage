"""
Pytest configuration for integration tests.

Requires the backend to be running (either locally or via Docker).
Set BACKEND_TEST_URL env var to override the default (http://localhost:8000).

Run with: pytest tests/ -v
"""
import os
import pytest
import httpx

BASE_URL = os.getenv("BACKEND_TEST_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def client():
    """Shared synchronous HTTP client for all tests."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def check_server(client):
    """Fail fast if the backend is not reachable before running any test."""
    try:
        r = client.get("/health")
        r.raise_for_status()
    except Exception as exc:
        pytest.exit(
            f"Backend not reachable at {BASE_URL}/health — start it first.\n{exc}",
            returncode=1,
        )
