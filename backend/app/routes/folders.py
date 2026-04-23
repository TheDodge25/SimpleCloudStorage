from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.database import get_db
from app.models.folder import CreateFolderRequest, FolderResponse, doc_to_folder_response
from app.storage import get_storage

router = APIRouter(prefix="/api/v1/folders", tags=["folders"])


async def _get_parent_path(db, parent_id: str | None) -> str:
    """Resolve the materialized path of the parent folder."""
    if parent_id is None:
        return ""
    parent = await db.folders.find_one({"_id": ObjectId(parent_id)})
    if not parent:
        raise HTTPException(404, "Parent folder not found")
    return parent["path"]


@router.post("", response_model=FolderResponse, status_code=201)
async def create_folder(body: CreateFolderRequest):
    db = get_db()

    parent_path = await _get_parent_path(db, body.parent_id)

    duplicate = await db.folders.find_one({
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
    }
    result = await db.folders.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc_to_folder_response(doc)


@router.get("", response_model=list[FolderResponse])
async def list_folders(parent_id: str | None = Query(default=None)):
    db = get_db()
    flt = {"parent_id": ObjectId(parent_id) if parent_id else None}
    cursor = db.folders.find(flt)
    return [doc_to_folder_response(doc) async for doc in cursor]


async def _collect_folder_ids(db, root_id: ObjectId) -> list[ObjectId]:
    """BFS to collect root and all descendant folder ObjectIds."""
    ids, queue = [root_id], [root_id]
    while queue:
        children = db.folders.find({"parent_id": {"$in": queue}})
        queue = [doc["_id"] async for doc in children]
        ids.extend(queue)
    return ids


@router.delete("/{folder_id}", status_code=204)
async def delete_folder(folder_id: str):
    db = get_db()
    storage = get_storage()

    folder_oid = ObjectId(folder_id)
    if not await db.folders.find_one({"_id": folder_oid}):
        raise HTTPException(404, "Folder not found")

    all_ids = await _collect_folder_ids(db, folder_oid)

    file_cursor = db.files.find({"folder_id": {"$in": all_ids}})
    async for file_doc in file_cursor:
        storage.remove_object(settings.minio_bucket_name, file_doc["minio_object_name"])

    await db.files.delete_many({"folder_id": {"$in": all_ids}})
    await db.folders.delete_many({"_id": {"$in": all_ids}})


@router.get("/{folder_id}/breadcrumb", response_model=list[FolderResponse])
async def get_breadcrumb(folder_id: str):
    db = get_db()
    crumbs, current_id = [], ObjectId(folder_id)
    while current_id:
        doc = await db.folders.find_one({"_id": current_id})
        if not doc:
            break
        crumbs.insert(0, doc_to_folder_response(doc))
        current_id = doc.get("parent_id")
    return crumbs
