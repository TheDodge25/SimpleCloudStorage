import re
from bson import ObjectId
from fastapi import APIRouter, Query

from app.database import get_db
from app.models.file import FileResponse, doc_to_file_response

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("", response_model=list[FileResponse])
async def search_files(
    q: str = Query(min_length=1),
    folder_id: str | None = Query(default=None),
):
    db = get_db()
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    flt: dict = {"original_name": {"$regex": pattern}}

    if folder_id is not None:
        flt["folder_id"] = ObjectId(folder_id)

    cursor = db.files.find(flt)
    return [doc_to_file_response(doc) async for doc in cursor]
