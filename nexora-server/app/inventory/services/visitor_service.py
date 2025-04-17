import logging
from typing import List
from flask import request
from app.core.schemas.visitor import VisitorCreate, VisitorUpdate
from app.core.services.base_service import BaseService
from app.core.s3.minio_client import minio_client
from app.shared.exceptions import BadRequestException

logger = logging.getLogger(__name__)


class VisitorService(BaseService[VisitorCreate]):
    def __init__(self):
        super().__init__(
            collection_name="visitors",
            create_schema=VisitorCreate,
            update_schema=VisitorUpdate
        )

    def create(self, data: VisitorCreate, tenant_id: str, query_params: dict = None) -> dict:
        """Create a visitor with image uploads."""
        # Handle image uploads
        image_urls = self._process_images(tenant_id)
        if data.images:
            image_urls.extend([minio_client.download_and_upload_image(
                tenant_id, url) for url in data.images])

        # Update data with processed image URLs
        data_dict = data.model_dump()
        data_dict["images"] = image_urls

        try:
            logger.debug(
                f"Creating visitor for tenant {tenant_id}: {data_dict}")
            return super().create(VisitorCreate(**data_dict), tenant_id, query_params)
        except Exception as e:
            logger.error(f"Failed to create visitor: {str(e)}")
            raise BadRequestException(f"Failed to create visitor: {str(e)}")

    def update(self, id: str, data: VisitorUpdate, tenant_id: str, query_params: dict = None) -> dict:
        """Update a visitor with image uploads."""
        # Handle image uploads
        image_urls = self._process_images(tenant_id)
        if data.images:
            image_urls.extend([minio_client.download_and_upload_image(
                tenant_id, url) for url in data.images])

        # Update data with processed image URLs
        data_dict = data.model_dump(exclude_unset=True)
        if image_urls:
            data_dict["images"] = image_urls

        try:
            logger.debug(
                f"Updating visitor {id} for tenant {tenant_id}: {data_dict}")
            return super().update(id, VisitorUpdate(**data_dict), tenant_id, query_params)
        except Exception as e:
            logger.error(f"Failed to update visitor {id}: {str(e)}")
            raise BadRequestException(f"Failed to update visitor: {str(e)}")

    def _process_images(self, tenant_id: str) -> List[str]:
        """Process uploaded image files and return MinIO URLs."""
        image_urls = []
        if "images" in request.files:
            for image in request.files.getlist("images"):
                if image and image.filename:
                    image_data = image.stream
                    image_name = image.filename
                    url = minio_client.upload_image(
                        tenant_id, image_data, image_name)
                    image_urls.append(url)
        return image_urls


# Singleton instance
visitor_service = VisitorService()
