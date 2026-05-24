import uuid
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.database import get_db
from app.storage import get_storage
from app.config import settings
from app.models.file import FileResponse, doc_to_file_response
from app.models.user import UserResponse

router = APIRouter(prefix="/api/v1/files", tags=["files"])


def _build_filter(owner_id: str, folder_id: str | None) -> dict:
    flt: dict = {"owner_id": ObjectId(owner_id)}
    if folder_id is None:
        flt["folder_id"] = None
    else:
        flt["folder_id"] = ObjectId(folder_id)
    return flt


async def _unique_name(db, owner_id: str, original: str, folder_id: str | None) -> str:
    """Return original name or 'name (N).ext' if a duplicate exists for this owner."""
    base, _, ext = original.rpartition(".")
    ext = f".{ext}" if ext and "." not in original[: original.rfind(".")] else (f".{ext}" if ext else "")
    if not base:
        base, ext = original, ""

    candidate = original
    counter = 1
    flt = _build_filter(owner_id, folder_id)
    while await db.files.find_one({**flt, "original_name": candidate}):
        candidate = f"{base} ({counter}){ext}"
        counter += 1
    return candidate


@router.get("", response_model=list[FileResponse])
async def list_files(
    folder_id: str | None = Query(default=None),
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    cursor = db.files.find(_build_filter(current_user.id, folder_id))
    return [doc_to_file_response(doc) async for doc in cursor]


@router.post("/upload", response_model=FileResponse, status_code=201)
async def upload_file(
    folder_id: str | None = Query(default=None),
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
):
    if file.size and file.size > settings.max_upload_size_bytes:
        raise HTTPException(413, "File exceeds maximum allowed size")

    # Quota check
    if file.size and (current_user.used_bytes + file.size) > current_user.quota_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Upload would exceed your storage quota "
                f"({current_user.quota_bytes // (1024**3)} GB). "
                f"Free up space or ask an admin to increase your quota."
            ),
        )

    db = get_db()
    storage = get_storage()

    original_name = await _unique_name(db, current_user.id, file.filename or "untitled", folder_id)
    object_name = f"uploads/{uuid.uuid4()}-{original_name}"

    storage.put_object(
        settings.minio_bucket_name,
        object_name,
        file.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=file.content_type or "application/octet-stream",
    )

    doc = {
        "filename": object_name,
        "original_name": original_name,
        "size": file.size or 0,
        "content_type": file.content_type or "application/octet-stream",
        "upload_date": datetime.now(timezone.utc),
        "minio_object_name": object_name,
        "folder_id": ObjectId(folder_id) if folder_id else None,
        "owner_id": ObjectId(current_user.id),
    }
    result = await db.files.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Increment used_bytes on the user
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$inc": {"used_bytes": file.size or 0}},
    )

    return doc_to_file_response(doc)


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    storage = get_storage()

    doc = await db.files.find_one({
        "_id": ObjectId(file_id),
        "owner_id": ObjectId(current_user.id),
    })
    if not doc:
        raise HTTPException(404, "File not found")

    response = storage.get_object(settings.minio_bucket_name, doc["minio_object_name"])
    return StreamingResponse(
        response.stream(32 * 1024),
        media_type=doc["content_type"],
        headers={"Content-Disposition": f'attachment; filename="{doc["original_name"]}"'},
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    storage = get_storage()

    doc = await db.files.find_one({
        "_id": ObjectId(file_id),
        "owner_id": ObjectId(current_user.id),
    })
    if not doc:
        raise HTTPException(404, "File not found")

    storage.remove_object(settings.minio_bucket_name, doc["minio_object_name"])
    await db.files.delete_one({"_id": ObjectId(file_id)})

    # Decrement used_bytes on the user
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$inc": {"used_bytes": -(doc.get("size") or 0)}},
    )
