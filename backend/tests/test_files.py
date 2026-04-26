"""Integration tests for /api/v1/files endpoints."""
import io
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def upload_file(client, filename="test.txt", content=b"hello drive", folder_id=None):
    params = {"folder_id": folder_id} if folder_id else {}
    return client.post(
        "/api/v1/files/upload",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        params=params,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFileUpload:
    def test_upload_returns_201(self, client):
        r = upload_file(client)
        assert r.status_code == 201

    def test_upload_response_has_required_fields(self, client):
        r = upload_file(client, "fields_check.txt")
        body = r.json()
        for field in ("id", "original_name", "size", "content_type", "upload_date"):
            assert field in body, f"Missing field: {field}"

    def test_upload_duplicate_auto_renames(self, client):
        upload_file(client, "dupe.txt")
        r2 = upload_file(client, "dupe.txt")
        assert r2.status_code == 201
        assert r2.json()["original_name"] != "dupe.txt"


class TestFileList:
    def test_list_root_returns_200(self, client):
        r = client.get("/api/v1/files")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_uploaded_file_appears_in_list(self, client):
        upload_file(client, "listcheck.txt")
        names = [f["original_name"] for f in client.get("/api/v1/files").json()]
        assert any("listcheck" in n for n in names)


class TestFileDownload:
    def test_download_returns_200(self, client):
        file_id = upload_file(client, "dl.txt", b"download me").json()["id"]
        r = client.get(f"/api/v1/files/{file_id}/download")
        assert r.status_code == 200
        assert r.content == b"download me"

    def test_download_unknown_id_returns_404(self, client):
        r = client.get("/api/v1/files/000000000000000000000000/download")
        assert r.status_code == 404


class TestFileDelete:
    def test_delete_returns_204(self, client):
        file_id = upload_file(client, "todelete.txt").json()["id"]
        r = client.delete(f"/api/v1/files/{file_id}")
        assert r.status_code == 204

    def test_deleted_file_not_in_list(self, client):
        file_id = upload_file(client, "gone.txt").json()["id"]
        client.delete(f"/api/v1/files/{file_id}")
        ids = [f["id"] for f in client.get("/api/v1/files").json()]
        assert file_id not in ids

    def test_delete_unknown_id_returns_404(self, client):
        r = client.delete("/api/v1/files/000000000000000000000000")
        assert r.status_code == 404
