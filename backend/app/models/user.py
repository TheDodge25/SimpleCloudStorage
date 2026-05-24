from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class UserDocument(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: str
    hashed_password: str
    role: Literal["user", "admin"] = "user"
    created_at: datetime
    quota_bytes: int
    used_bytes: int = 0
    # Hashed refresh tokens currently valid for this user (for revocation)
    refresh_token_hashes: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class UserResponse(BaseModel):
    """Safe public projection — never exposes the password hash."""
    id: str
    username: str
    email: str
    role: Literal["user", "admin"]
    created_at: datetime
    quota_bytes: int
    used_bytes: int


class TokenPayload(BaseModel):
    """Claims carried inside a JWT."""
    sub: str          # user _id as string
    role: Literal["user", "admin"]
    type: Literal["access", "refresh"]
    jti: str          # unique token ID (UUID4) — used for refresh token revocation


def doc_to_user_response(doc: dict) -> UserResponse:
    return UserResponse(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"],
        role=doc["role"],
        created_at=doc["created_at"],
        quota_bytes=doc["quota_bytes"],
        used_bytes=doc.get("used_bytes", 0),
    )
