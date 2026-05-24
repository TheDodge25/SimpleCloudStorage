from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models.folder import CreateFolderRequest, FolderResponse, doc_to_folder_response
from app.models.user import UserResponse
from app.storage import get_storage

router = APIRouter(prefix="/api/v1/folders", tags=["folders"])


async def _get_parent_path(db, owner_id: str, parent_id: str | None) -> str:
    """Resolve the materialized path of the parent folder (must belong to the same owner)."""
    if parent_id is None:
        return ""
    parent = await db.folders.find_one({
        "_id": ObjectId(parent_id),
        "owner_id": ObjectId(owner_id),
    })
    if not parent:
        raise HTTPException(404, "Parent folder not found")
    return parent["path"]


@router.post("", response_model=FolderResponse, status_code=201)
async def create_folder(
    body: CreateFolderRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()

    parent_path = await _get_parent_path(db, current_user.id, body.parent_id)

    duplicate = await db.folders.find_one({
        "owner_id": ObjectId(current_user.id),
        "parent_id": ObjectId(body.parent_id) if body.parent_id else None,
        "name": body.name,
    })
    if duplicate:
        raise HTTPException(409, f"A folder named '{body.name}' already exists here")

    path = f"{parent_path}/{body.name}"
    doc = {
        "name": body.name,
        "parent_id": ObjectId(body.parent_id) if body.parent_id else None,
        "created_date": datetime.now(timezone.utc),
        "path": path,
        "owner_id": ObjectId(current_user.id),
    }
    result = await db.folders.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc_to_folder_response(doc)


@router.get("", response_model=list[FolderResponse])
async def list_folders(
    parent_id: str | None = Query(default=None),
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    flt: dict = {"owner_id": ObjectId(current_user.id)}
    flt["parent_id"] = ObjectId(parent_id) if parent_id else None
    cursor = db.folders.find(flt)
    return [doc_to_folder_response(doc) async for doc in cursor]


async def _collect_folder_ids(db, owner_id: str, root_id: ObjectId) -> list[ObjectId]:
    """BFS to collect root and all descendant folder ObjectIds for this owner."""
    ids, queue = [root_id], [root_id]
    while queue:
        children = db.folders.find({"owner_id": ObjectId(owner_id), "parent_id": {"$in": queue}})
        queue = [doc["_id"] async for doc in children]
        ids.extend(queue)
    return ids


@router.delete("/{folder_id}", status_code=204)
async def delete_folder(
    folder_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    storage = get_storage()

    folder_oid = ObjectId(folder_id)
    if not await db.folders.find_one({"_id": folder_oid, "owner_id": ObjectId(current_user.id)}):
        raise HTTPException(404, "Folder not found")

    all_ids = await _collect_folder_ids(db, current_user.id, folder_oid)

    total_freed = 0
    file_cursor = db.files.find({"owner_id": ObjectId(current_user.id), "folder_id": {"$in": all_ids}})
    async for file_doc in file_cursor:
        storage.remove_object(settings.minio_bucket_name, file_doc["minio_object_name"])
        total_freed += file_doc.get("size") or 0

    await db.files.delete_many({"owner_id": ObjectId(current_user.id), "folder_id": {"$in": all_ids}})
    await db.folders.delete_many({"_id": {"$in": all_ids}})

    # Decrement used_bytes
    if total_freed:
        await db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$inc": {"used_bytes": -total_freed}},
        )


@router.get("/{folder_id}/breadcrumb", response_model=list[FolderResponse])
async def get_breadcrumb(
    folder_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    crumbs, current_id = [], ObjectId(folder_id)
    while current_id:
        doc = await db.folders.find_one({"_id": current_id, "owner_id": ObjectId(current_user.id)})
        if not doc:
            break
        crumbs.insert(0, doc_to_folder_response(doc))
        current_id = doc.get("parent_id")
    return crumbs
