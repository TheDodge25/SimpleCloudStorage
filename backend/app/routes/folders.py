from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.database import get_db
from app.models.folder import CreateFolderRequest, FolderResponse, doc_to_folder_response

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
