"""
auth.py — centralised authentication helpers and FastAPI dependencies.

Provides:
  - Password hashing / verification (bcrypt via passlib)
  - JWT access + refresh token creation and decoding (python-jose)
  - get_current_user   dependency → injects the current UserDocument
  - require_admin      dependency → same but raises 403 if not admin
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.database import get_db
from app.models.user import TokenPayload, UserResponse, doc_to_user_response

# ── Password hashing ──────────────────────────────────────────────────────────

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def _make_token(user_id: str, role: str, token_type: str, expires_delta: timedelta) -> tuple[str, str]:
    """
    Create a signed JWT.
    Returns (encoded_token, jti) so the caller can store jti for refresh tokens.
    """
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": now + expires_delta,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti


def create_access_token(user_id: str, role: str) -> str:
    token, _ = _make_token(
        user_id, role, "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    return token


def create_refresh_token(user_id: str, role: str) -> tuple[str, str]:
    """Returns (refresh_token, jti). Caller must persist the jti hash in the DB."""
    return _make_token(
        user_id, role, "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT. Raises HTTPException 401 on any failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return TokenPayload(**payload)
    except (JWTError, Exception):
        raise credentials_exception


# ── FastAPI dependencies ──────────────────────────────────────────────────────

async def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> UserResponse:
    """
    Read the access_token HttpOnly cookie, validate it, and return the user.
    Raises 401 if the token is missing or invalid.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_token(access_token)

    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    from bson import ObjectId

    db = get_db()
    doc = await db.users.find_one({"_id": ObjectId(payload.sub)})
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return doc_to_user_response(doc)


async def require_admin(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Extend get_current_user — raises 403 if the caller is not an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
