"""
routes/auth.py — login, token refresh, logout, and /me endpoints.

All tokens are delivered as HttpOnly, SameSite=Lax cookies so they are
never accessible to JavaScript and are not vulnerable to XSS theft.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_password,
)
from app.config import settings
from app.database import get_db
from app.models.user import UserResponse, doc_to_user_response

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# ── Cookie helpers ────────────────────────────────────────────────────────────

_COOKIE_OPTS = dict(httponly=True, samesite="lax", secure=False)
# Set secure=True in production (HTTPS). Can be driven by an env var later.


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.access_token_expire_minutes * 60,
        **_COOKIE_OPTS,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.refresh_token_expire_days * 86400,
        **_COOKIE_OPTS,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


# ── Request / response schemas ────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    user: UserResponse


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, response: Response):
    db = get_db()
    doc = await db.users.find_one({"username": body.username})
    if not doc or not verify_password(body.password, doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user_id = str(doc["_id"])
    access_token = create_access_token(user_id, doc["role"])
    refresh_token, jti = create_refresh_token(user_id, doc["role"])

    # Store hashed jti for revocation support
    from passlib.context import CryptContext
    _ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    jti_hash = _ctx.hash(jti)
    await db.users.update_one(
        {"_id": doc["_id"]},
        {
            "$push": {"refresh_token_hashes": jti_hash},
            "$set": {"last_login": datetime.now(timezone.utc)},
        },
    )

    _set_auth_cookies(response, access_token, refresh_token)
    return {"user": doc_to_user_response(doc)}


@router.post("/refresh", response_model=AuthResponse)
async def refresh(response: Response, refresh_token: str | None = Cookie(default=None)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    payload = decode_token(refresh_token)
    if payload.type != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    db = get_db()
    doc = await db.users.find_one({"_id": ObjectId(payload.sub)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Verify jti is in the stored hash list (token hasn't been revoked)
    from passlib.context import CryptContext
    _ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    valid = any(_ctx.verify(payload.jti, h) for h in doc.get("refresh_token_hashes", []))
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    # Rotate: remove old jti hash, issue new token pair
    old_hashes = [h for h in doc.get("refresh_token_hashes", []) if not _ctx.verify(payload.jti, h)]
    new_access = create_access_token(payload.sub, doc["role"])
    new_refresh, new_jti = create_refresh_token(payload.sub, doc["role"])
    new_hash = _ctx.hash(new_jti)

    await db.users.update_one(
        {"_id": doc["_id"]},
        {"$set": {"refresh_token_hashes": old_hashes + [new_hash]}},
    )

    _set_auth_cookies(response, new_access, new_refresh)
    return {"user": doc_to_user_response(doc)}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    current_user: UserResponse = Depends(get_current_user),
):
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            from passlib.context import CryptContext
            _ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
            db = get_db()
            doc = await db.users.find_one({"_id": ObjectId(payload.sub)})
            if doc:
                remaining = [
                    h for h in doc.get("refresh_token_hashes", [])
                    if not _ctx.verify(payload.jti, h)
                ]
                await db.users.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"refresh_token_hashes": remaining}},
                )
        except Exception:
            pass  # Token already invalid — still clear cookies

    _clear_auth_cookies(response)


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
