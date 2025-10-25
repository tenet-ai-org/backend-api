from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class UploadStartRequest(BaseModel):
    file_name: str
    size: int
    file_type: str = "PDF"


class UploadStartResponse(BaseModel):
    document_id: str
    part_size_in_bytes: int


class PartUrlResponse(BaseModel):
    url: str
    expiration: datetime


class PartInfo(BaseModel):
    part_number: int
    etag: str


class UploadCompleteRequest(BaseModel):
    document_id: str
    parts: List[PartInfo]


class UploadCompleteResponse(BaseModel):
    document_id: str
