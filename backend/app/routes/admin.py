"""
routes/admin.py — admin-only user management endpoints.

All endpoints require the caller to have role="admin".
Admins can create users, list users, view a single user,
update a user's quota or role, and delete a user (along with their files).
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import hash_password, require_admin
from app.config import settings
from app.database import get_db
from app.models.user import UserResponse, doc_to_user_response
from app.storage import get_storage

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ── Request schemas ───────────────────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8)
    role: str = "user"
    quota_bytes: int | None = None  # falls back to DEFAULT_QUOTA_BYTES


class UpdateUserRequest(BaseModel):
    quota_bytes: int | None = None
    role: str | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserResponse])
async def list_users(_admin=Depends(require_admin)):
    db = get_db()
    cursor = db.users.find({})
    return [doc_to_user_response(doc) async for doc in cursor]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, _admin=Depends(require_admin)):
    db = get_db()
    doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return doc_to_user_response(doc)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: CreateUserRequest, _admin=Depends(require_admin)):
    db = get_db()

    if await db.users.find_one({"username": body.username}):
        raise HTTPException(status_code=409, detail="Username already taken")
    if await db.users.find_one({"email": body.email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    if body.role not in ("user", "admin"):
        raise HTTPException(status_code=422, detail="role must be 'user' or 'admin'")

    doc = {
        "username": body.username,
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "role": body.role,
        "created_at": datetime.now(timezone.utc),
        "quota_bytes": body.quota_bytes if body.quota_bytes is not None else settings.default_quota_bytes,
        "used_bytes": 0,
        "refresh_token_hashes": [],
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc_to_user_response(doc)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, body: UpdateUserRequest, _admin=Depends(require_admin)):
    db = get_db()
    doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")

    updates: dict = {}
    if body.quota_bytes is not None:
        updates["quota_bytes"] = body.quota_bytes
    if body.role is not None:
        if body.role not in ("user", "admin"):
            raise HTTPException(status_code=422, detail="role must be 'user' or 'admin'")
        updates["role"] = body.role

    if updates:
        await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})

    updated = await db.users.find_one({"_id": ObjectId(user_id)})
    return doc_to_user_response(updated)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, _admin=Depends(require_admin)):
    db = get_db()
    storage = get_storage()

    doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete all files owned by this user from MinIO and MongoDB
    owner_oid = ObjectId(user_id)
    async for file_doc in db.files.find({"owner_id": owner_oid}):
        try:
            storage.remove_object(settings.minio_bucket_name, file_doc["minio_object_name"])
        except Exception:
            pass  # Best-effort — continue even if MinIO object is missing

    await db.files.delete_many({"owner_id": owner_oid})
    await db.folders.delete_many({"owner_id": owner_oid})
    await db.users.delete_one({"_id": owner_oid})
