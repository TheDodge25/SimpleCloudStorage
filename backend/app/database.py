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
    # files indexes
    await db.files.create_index("folder_id")
    await db.files.create_index("original_name")
    # folders indexes
    await db.folders.create_index("parent_id")
    await db.folders.create_index("path")


async def close_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
