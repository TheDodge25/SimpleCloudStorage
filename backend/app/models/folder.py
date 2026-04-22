from datetime import datetime
from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_id: str | None = None


class FolderResponse(BaseModel):
    id: str
    name: str
    parent_id: str | None = None
    created_date: datetime
    path: str


def doc_to_folder_response(doc: dict) -> FolderResponse:
    return FolderResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        parent_id=str(doc["parent_id"]) if doc.get("parent_id") else None,
        created_date=doc["created_date"],
        path=doc["path"],
    )
