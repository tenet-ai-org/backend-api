import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        
        try:
            self.client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
    
    def create_multipart_upload(self, bucket_name: str, file_name: str) -> str:
        # TODO: user_id will be passed when we implement auth/JWT
        user_id = "user_123"
        key = f"{user_id}/{file_name}"
        response = self.client.create_multipart_upload(
            Bucket=bucket_name,
            Key=key,
            ContentType="application/pdf"
        )
        return response['UploadId']
    
    def generate_presigned_url(self, bucket_name: str, file_name: str, upload_id: str, part_number: int) -> str:
        # TODO: user_id will be passed when we implement auth/JWT
        user_id = "user_123"
        key = f"{user_id}/{file_name}"
        response = self.client.generate_presigned_url(
            'upload_part',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'UploadId': upload_id,
                'PartNumber': part_number
            },
            ExpiresIn=3600
        )
        return response
    
    def complete_multipart_upload(self, bucket_name: str, file_name: str, upload_id: str, parts: list) -> str:
        # TODO: user_id will be passed when we implement auth/JWT
        user_id = "user_123"
        key = f"{user_id}/{file_name}"
        response = self.client.complete_multipart_upload(
            Bucket=bucket_name,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        return response['Location']


s3_client: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    global s3_client
    if s3_client is None:
        s3_client = S3Client()
    return s3_client
