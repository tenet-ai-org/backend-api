from fastapi import FastAPI, HTTPException, Query
import uuid
import logging
import os
from datetime import datetime, timedelta

from models.uploads import (
    UploadStartRequest, UploadStartResponse,
    PartUrlResponse, UploadCompleteRequest, UploadCompleteResponse
)
from clients.s3_client import get_s3_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TenetAI Backend API", version="1.0.0")

# Store upload sessions in-memory # TODO: ttl cache (+ optionally aborts upload)
upload_sessions = {}

# TODO: make this configurable or plumb from CDK for explicit contract
upload_bucket_name = "uploaded-doc-bucket"

@app.get("/")
async def root():
    return {"greeting": "Welcome to TenetAI"}

@app.post("/uploads/start", response_model=UploadStartResponse)
async def start_upload(request: UploadStartRequest):
    document_id = str(uuid.uuid4())
    s3_client = get_s3_client()
    bucket_name = upload_bucket_name
    
    upload_id = s3_client.create_multipart_upload(
        bucket_name=bucket_name,
        file_name=request.file_name
    )
    
    upload_sessions[document_id] = {
        "upload_id": upload_id,
        "file_name": request.file_name
    }
    
    return UploadStartResponse(
        document_id=document_id,
        part_size_in_bytes=10485760
    )

@app.get("/uploads/part-url", response_model=PartUrlResponse)
async def get_part_url(document_id: str = Query(...), part_number: int = Query(...)):
    if document_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = upload_sessions[document_id]
    s3_client = get_s3_client()
    bucket_name = upload_bucket_name
    
    url = s3_client.generate_presigned_url(
        bucket_name=bucket_name,
        file_name=session["file_name"],
        upload_id=session["upload_id"],
        part_number=part_number
    )
    
    expiration = datetime.utcnow() + timedelta(hours=1)
    
    return PartUrlResponse(url=url, expiration=expiration)

@app.post("/uploads/complete", response_model=UploadCompleteResponse)
async def complete_upload(request: UploadCompleteRequest):
    if request.document_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = upload_sessions[request.document_id]
    s3_client = get_s3_client()
    bucket_name = upload_bucket_name
    
    parts = [{"ETag": part.etag, "PartNumber": part.part_number} for part in request.parts]
    
    s3_client.complete_multipart_upload(
        bucket_name=bucket_name,
        file_name=session["file_name"],
        upload_id=session["upload_id"],
        parts=parts
    )
    
    del upload_sessions[request.document_id]
    
    return UploadCompleteResponse(document_id=request.document_id)