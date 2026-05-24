from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_url)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongo_db_name]


async def create_indexes() -> None:
    db = get_db()

    # users indexes
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)

    # files indexes
    await db.files.create_index("folder_id")
    await db.files.create_index("original_name")
    await db.files.create_index("owner_id")

    # folders indexes
    await db.folders.create_index("parent_id")
    await db.folders.create_index("path")
    await db.folders.create_index("owner_id")

    # shares indexes
    await db.shares.create_index("file_id")
    await db.shares.create_index("token", unique=True, sparse=True)
    await db.shares.create_index("shared_with_user_id", sparse=True)


async def close_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
