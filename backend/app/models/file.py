from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class FileDocument(BaseModel):
    id: str = Field(alias="_id")
    filename: str
    original_name: str
    size: int
    content_type: str
    upload_date: datetime
    minio_object_name: str
    folder_id: str | None = None
    owner_id: str

    model_config = {"populate_by_name": True}


class FileResponse(BaseModel):
    id: str
    original_name: str
    size: int
    content_type: str
    upload_date: datetime
    folder_id: str | None = None
    owner_id: str


def doc_to_file_response(doc: dict) -> FileResponse:
    return FileResponse(
        id=str(doc["_id"]),
        original_name=doc["original_name"],
        size=doc["size"],
        content_type=doc["content_type"],
        upload_date=doc["upload_date"],
        folder_id=str(doc["folder_id"]) if doc.get("folder_id") else None,
        owner_id=str(doc["owner_id"]),
    )
