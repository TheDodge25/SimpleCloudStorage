"""Integration tests for /api/v1/search endpoint."""
import io
import pytest


def upload(auth_client, filename, content=b"search test content"):
    return auth_client.post(
        "/api/v1/files/upload",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
    )


class TestSearch:
    def test_search_requires_auth(self, unauth_client):
        r = unauth_client.get("/api/v1/search", params={"q": "test"})
        assert r.status_code == 401

    def test_search_returns_200(self, auth_client):
        r = auth_client.get("/api/v1/search", params={"q": "test"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_search_finds_uploaded_file(self, auth_client):
        upload(auth_client, "unique_search_target.txt")
        r = auth_client.get("/api/v1/search", params={"q": "unique_search_target"})
        names = [f["original_name"] for f in r.json()]
        assert any("unique_search_target" in n for n in names)

    def test_search_is_case_insensitive(self, auth_client):
        upload(auth_client, "CaseTest.txt")
        r = auth_client.get("/api/v1/search", params={"q": "casetest"})
        names = [f["original_name"] for f in r.json()]
        assert any("CaseTest" in n for n in names)

    def test_search_no_results_returns_empty_list(self, auth_client):
        r = auth_client.get("/api/v1/search", params={"q": "zzz_no_match_xyz_999"})
        assert r.status_code == 200
        assert r.json() == []

    def test_search_missing_query_returns_422(self, auth_client):
        r = auth_client.get("/api/v1/search")
        assert r.status_code == 422

    def test_search_scoped_to_folder(self, auth_client):
        folder_id = auth_client.post(
            "/api/v1/folders", json={"name": "SearchScope", "parent_id": None}
        ).json()["id"]
        auth_client.post(
            "/api/v1/files/upload",
            files={"file": ("scoped_file.txt", io.BytesIO(b"x"), "text/plain")},
            params={"folder_id": folder_id},
        )
        r = auth_client.get("/api/v1/search", params={"q": "scoped_file", "folder_id": folder_id})
        assert r.status_code == 200
        assert len(r.json()) >= 1
