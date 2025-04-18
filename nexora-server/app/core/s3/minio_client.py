import logging
import json
import os
import uuid
from minio import Minio
from minio.error import S3Error
from urllib.parse import urlparse
import requests
from io import BytesIO
from datetime import timedelta
from app.shared.exceptions import InternalServerException

logger = logging.getLogger(__name__)


class MinioClient:
    def __init__(self):
        # Load credentials from app/core/s3/credentials.json
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(current_dir, "credentials.json")
            with open(credentials_path, "r") as f:
                creds = json.load(f)
            self.access_key = creds["accessKey"]
            self.secret_key = creds["secretKey"]
            # Configurable bucket name
            self.bucket_name = creds.get("bucket_name", "nexora")
            self.url = "http://127.0.0.1:9000"  # S3 API endpoint
            logger.debug(f"Loaded MinIO credentials from {credentials_path}")
        except Exception as e:
            logger.error(f"Failed to load MinIO credentials: {str(e)}")
            raise InternalServerException(
                f"Failed to initialize MinIO client: {str(e)}")

        # Initialize MinIO client
        self.client = Minio(
            "127.0.0.1:9000",
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False  # Set to True if using HTTPS
        )

        # Ensure bucket exists
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to create MinIO bucket: {str(e)}")
            raise InternalServerException(
                f"Failed to initialize MinIO bucket: {str(e)}")

    def upload_image(self, tenant_id: str, image_data: BytesIO, image_name: str) -> str:
        """Upload an image to MinIO and return a presigned URL."""
        object_path = f"{tenant_id}/images/{image_name}"
        try:
            # Upload the image
            self.client.put_object(
                self.bucket_name,
                object_path,
                image_data,
                length=-1,  # Unknown length, let MinIO handle chunking
                part_size=10*1024*1024,  # 10MB part size, as in app.py
                content_type="image/jpeg"  # Adjust based on image type
            )
            # Generate presigned URL
            presigned_url = self.client.get_presigned_url(
                "GET",
                self.bucket_name,
                object_path,
                expires=timedelta(minutes=10)
            )
            logger.debug(f"Uploaded image to MinIO: {presigned_url}")
            return presigned_url
        except S3Error as e:
            logger.error(f"Failed to upload image to MinIO: {str(e)}")
            raise InternalServerException(f"Failed to upload image: {str(e)}")

    def download_and_upload_image(self, tenant_id: str, image_url: str) -> str:
        """Download an image from a URL and upload to MinIO."""
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            filename = os.path.basename(urlparse(image_url).path).split("?")[
                0] or f"image_{uuid.uuid4()}.jpg"
            return self.upload_image(tenant_id, image_data, filename)
        except requests.RequestException as e:
            logger.error(
                f"Failed to download image from {image_url}: {str(e)}")
            raise InternalServerException(
                f"Failed to download image: {str(e)}")


# Singleton instance
minio_client = MinioClient()
