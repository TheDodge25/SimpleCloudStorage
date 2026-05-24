"""Integration tests for /api/v1/files endpoints."""
import io
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def upload_file(auth_client, filename="test.txt", content=b"hello drive", folder_id=None):
    params = {"folder_id": folder_id} if folder_id else {}
    return auth_client.post(
        "/api/v1/files/upload",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        params=params,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFileUpload:
    def test_upload_requires_auth(self, unauth_client):
        r = unauth_client.post("/api/v1/files/upload", files={"file": ("test.txt", io.BytesIO(b""), "text/plain")})
        assert r.status_code == 401

    def test_upload_returns_201(self, auth_client):
        r = upload_file(auth_client)
        assert r.status_code == 201

    def test_upload_response_has_required_fields(self, auth_client):
        r = upload_file(auth_client, "fields_check.txt")
        body = r.json()
        for field in ("id", "original_name", "size", "content_type", "upload_date", "owner_id"):
            assert field in body, f"Missing field: {field}"

    def test_upload_duplicate_auto_renames(self, auth_client):
        upload_file(auth_client, "dupe.txt")
        r2 = upload_file(auth_client, "dupe.txt")
        assert r2.status_code == 201
        assert r2.json()["original_name"] != "dupe.txt"


class TestFileList:
    def test_list_root_returns_200(self, auth_client):
        r = auth_client.get("/api/v1/files")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_uploaded_file_appears_in_list(self, auth_client):
        upload_file(auth_client, "listcheck.txt")
        names = [f["original_name"] for f in auth_client.get("/api/v1/files").json()]
        assert any("listcheck" in n for n in names)


class TestFileDownload:
    def test_download_returns_200(self, auth_client):
        file_id = upload_file(auth_client, "dl.txt", b"download me").json()["id"]
        r = auth_client.get(f"/api/v1/files/{file_id}/download")
        assert r.status_code == 200
        assert r.content == b"download me"

    def test_download_unknown_id_returns_404(self, auth_client):
        r = auth_client.get("/api/v1/files/000000000000000000000000/download")
        assert r.status_code == 404


class TestFileDelete:
    def test_delete_returns_204(self, auth_client):
        file_id = upload_file(auth_client, "todelete.txt").json()["id"]
        r = auth_client.delete(f"/api/v1/files/{file_id}")
        assert r.status_code == 204

    def test_deleted_file_not_in_list(self, auth_client):
        file_id = upload_file(auth_client, "gone.txt").json()["id"]
        auth_client.delete(f"/api/v1/files/{file_id}")
        ids = [f["id"] for f in auth_client.get("/api/v1/files").json()]
        assert file_id not in ids

    def test_delete_unknown_id_returns_404(self, auth_client):
        r = auth_client.delete("/api/v1/files/000000000000000000000000")
        assert r.status_code == 404

class TestDataIsolation:
    def test_users_cannot_see_each_others_files(self, admin_client, auth_client):
        # auth_client uploads a file
        file_id = upload_file(auth_client, "secret.txt", b"secret").json()["id"]
        
        # admin_client tries to get the file list and should not see it
        # (Wait, admin client uses the normal file list endpoint, which is scoped to owner_id)
        admin_files = [f["id"] for f in admin_client.get("/api/v1/files").json()]
        assert file_id not in admin_files

        # admin_client tries to download the file directly
        r = admin_client.get(f"/api/v1/files/{file_id}/download")
        assert r.status_code == 404

        # admin_client tries to delete the file
        r = admin_client.delete(f"/api/v1/files/{file_id}")
        assert r.status_code == 404
