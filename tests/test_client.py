import requests
import os
import sys
import math
from typing import List, Tuple


class MultipartUploadClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.part_size = 5242880  # 5MB chunks 
    
    def split_file(self, file_path: str) -> List[bytes]:
        """Split file into chunks for multipart upload"""
        chunks = []
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.part_size)
                if not chunk:
                    break
                chunks.append(chunk)
        return chunks
    
    def upload_file(self, file_path: str) -> str:
        """Complete multipart upload workflow"""
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        print(f"Uploading {file_name} ({file_size:,} bytes)")
        
        # 1. Start upload
        print("1. Starting multipart upload...")
        start_response = requests.post(f"{self.base_url}/uploads/start", json={
            "file_name": file_name,
            "size": file_size,
            "file_type": "PDF"
        })
        start_response.raise_for_status()
        start_data = start_response.json()
        document_id = start_data["document_id"]
        part_size = start_data["part_size_in_bytes"]
        
        print(f"   Document ID: {document_id}")
        print(f"   Part size: {part_size:,} bytes")
        
        # 2. Split file into chunks
        print("2. Splitting file into chunks...")
        chunks = self.split_file(file_path)
        num_parts = len(chunks)
        print(f"   Split into {num_parts} parts")
        
        # 3. Upload each part
        print("3. Uploading parts...")
        parts = []
        for i, chunk in enumerate(chunks, 1):
            print(f"   Uploading part {i}/{num_parts} ({len(chunk):,} bytes)")
            
            # Get presigned URL
            url_response = requests.get(f"{self.base_url}/uploads/part-url", params={
                "document_id": document_id,
                "part_number": i
            })
            url_response.raise_for_status()
            url_data = url_response.json()
            presigned_url = url_data["url"]
            
            # Upload part directly to S3
            upload_response = requests.put(presigned_url, data=chunk)
            upload_response.raise_for_status()
            
            # Extract ETag from response headers
            etag = upload_response.headers.get('ETag', '').strip('"')
            parts.append({
                "part_number": i,
                "etag": etag
            })
            print(f"   Part {i} uploaded successfully (ETag: {etag})")
        
        # 4. Complete upload
        print("4. Completing multipart upload...")
        complete_response = requests.post(f"{self.base_url}/uploads/complete", json={
            "document_id": document_id,
            "parts": parts
        })
        complete_response.raise_for_status()
        complete_data = complete_response.json()
        
        print(f"✅ Upload completed successfully!")
        print(f"   Final document ID: {complete_data['document_id']}")
        
        return document_id


def test_multipart_upload(pdf_path: str):
    """Test the multipart upload functionality"""
    client = MultipartUploadClient()
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test file not found: {pdf_path}")
        return False
    
    try:
        document_id = client.upload_file(pdf_path)
        print(f"\n🎉 Test passed! Document uploaded with ID: {document_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Test failed with request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing multipart upload with backend API")
    print("=" * 50)
    
    # Get PDF path from command line argument or use default
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "tests/test_document_text.pdf"
    
    print(f"Using PDF file: {pdf_path}")
    
    success = test_multipart_upload(pdf_path)
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        exit(1)
