"""Integration tests for /api/v1/folders endpoints."""
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def create_folder(auth_client, name, parent_id=None):
    return auth_client.post(
        "/api/v1/folders",
        json={"name": name, "parent_id": parent_id},
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFolderCreate:
    def test_create_requires_auth(self, unauth_client):
        r = unauth_client.post("/api/v1/folders", json={"name": "test"})
        assert r.status_code == 401

    def test_create_returns_201(self, auth_client):
        r = create_folder(auth_client, "TestFolder")
        assert r.status_code == 201

    def test_create_response_has_required_fields(self, auth_client):
        r = create_folder(auth_client, "FieldsFolder")
        body = r.json()
        for field in ("id", "name", "parent_id", "created_date", "owner_id"):
            assert field in body, f"Missing field: {field}"

    def test_duplicate_name_in_same_parent_returns_409(self, auth_client):
        create_folder(auth_client, "DupFolder")
        r2 = create_folder(auth_client, "DupFolder")
        assert r2.status_code == 409

    def test_nested_folder_creation(self, auth_client):
        parent_id = create_folder(auth_client, "Parent").json()["id"]
        r = create_folder(auth_client, "Child", parent_id=parent_id)
        assert r.status_code == 201
        assert r.json()["parent_id"] == parent_id


class TestFolderList:
    def test_list_root_returns_200(self, auth_client):
        r = auth_client.get("/api/v1/folders")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_created_folder_appears_in_list(self, auth_client):
        create_folder(auth_client, "ListVisible")
        names = [f["name"] for f in auth_client.get("/api/v1/folders").json()]
        assert "ListVisible" in names


class TestFolderBreadcrumb:
    def test_breadcrumb_returns_path(self, auth_client):
        parent_id = create_folder(auth_client, "BreadParent").json()["id"]
        child_id = create_folder(auth_client, "BreadChild", parent_id=parent_id).json()["id"]
        r = auth_client.get(f"/api/v1/folders/{child_id}/breadcrumb")
        assert r.status_code == 200
        names = [c["name"] for c in r.json()]
        assert "BreadParent" in names
        assert "BreadChild" in names


class TestFolderDelete:
    def test_delete_returns_204(self, auth_client):
        folder_id = create_folder(auth_client, "ToDelete").json()["id"]
        r = auth_client.delete(f"/api/v1/folders/{folder_id}")
        assert r.status_code == 204

    def test_deleted_folder_not_in_list(self, auth_client):
        folder_id = create_folder(auth_client, "GoneFolder").json()["id"]
        auth_client.delete(f"/api/v1/folders/{folder_id}")
        ids = [f["id"] for f in auth_client.get("/api/v1/folders").json()]
        assert folder_id not in ids

    def test_delete_unknown_id_returns_404(self, auth_client):
        r = auth_client.delete("/api/v1/folders/000000000000000000000000")
        assert r.status_code == 404
