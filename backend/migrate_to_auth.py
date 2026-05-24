#!/usr/bin/env python3
"""
migrate_to_auth.py — one-time migration script.

Run this ONCE after deploying the auth system for the first time.
It will:
  1. Create an admin user (credentials taken from CLI args or env vars).
  2. Assign owner_id on all existing files and folders to that admin.
  3. Set the admin's used_bytes to the sum of all existing file sizes.

Usage:
  python migrate_to_auth.py --username admin --email admin@example.com --password <secret>

Or via environment variables:
  ADMIN_USERNAME=admin ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=secret python migrate_to_auth.py

The script is idempotent for user creation (skips if the username already exists)
but will overwrite owner_id on all files/folders unconditionally.
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

# ── Config (mirrors app/config.py but standalone so the script works outside Docker) ──
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "drivedb")
DEFAULT_QUOTA_BYTES = int(os.getenv("DEFAULT_QUOTA_BYTES", str(10 * 1024 * 1024 * 1024)))


async def migrate(username: str, email: str, password: str) -> None:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB_NAME]

    # ── 1. Create admin user (skip if already exists) ─────────────────────────
    existing = await db.users.find_one({"username": username})
    if existing:
        admin_id = existing["_id"]
        print(f"[migrate] User '{username}' already exists — skipping creation.")
    else:
        from app.auth import hash_password
        doc = {
            "username": username,
            "email": email,
            "hashed_password": hash_password(password),
            "role": "admin",
            "created_at": datetime.now(timezone.utc),
            "quota_bytes": DEFAULT_QUOTA_BYTES,
            "used_bytes": 0,
            "refresh_token_hashes": [],
        }
        result = await db.users.insert_one(doc)
        admin_id = result.inserted_id
        print(f"[migrate] Created admin user '{username}' with id={admin_id}.")

    # ── 2. Assign owner_id on all files ───────────────────────────────────────
    files_result = await db.files.update_many(
        {"owner_id": {"$exists": False}},
        {"$set": {"owner_id": admin_id}},
    )
    print(f"[migrate] Updated owner_id on {files_result.modified_count} file(s).")

    # ── 3. Assign owner_id on all folders ────────────────────────────────────
    folders_result = await db.folders.update_many(
        {"owner_id": {"$exists": False}},
        {"$set": {"owner_id": admin_id}},
    )
    print(f"[migrate] Updated owner_id on {folders_result.modified_count} folder(s).")

    # ── 4. Recalculate used_bytes for the admin ───────────────────────────────
    pipeline = [
        {"$match": {"owner_id": admin_id}},
        {"$group": {"_id": None, "total": {"$sum": "$size"}}},
    ]
    agg = await db.files.aggregate(pipeline).to_list(1)
    used_bytes = agg[0]["total"] if agg else 0
    await db.users.update_one({"_id": admin_id}, {"$set": {"used_bytes": used_bytes}})
    print(f"[migrate] Set used_bytes={used_bytes} ({used_bytes / (1024**3):.2f} GB) for '{username}'.")

    client.close()
    print("[migrate] Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="One-time auth migration script")
    parser.add_argument("--username", default=os.getenv("ADMIN_USERNAME", "admin"))
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "admin@localhost"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", ""))
    args = parser.parse_args()

    if not args.password:
        print("Error: --password is required (or set ADMIN_PASSWORD env var)", file=sys.stderr)
        sys.exit(1)

    asyncio.run(migrate(args.username, args.email, args.password))


if __name__ == "__main__":
    main()
