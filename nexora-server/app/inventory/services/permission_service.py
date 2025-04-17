import logging
from app.core.schemas.permission import PermissionCreate, PermissionUpdate
from app.core.services.base_service import BaseService

logger = logging.getLogger(__name__)

class PermissionService(BaseService[PermissionCreate]):
    def __init__(self):
        super().__init__(
            collection_name="permissions",
            create_schema=PermissionCreate,
            update_schema=PermissionUpdate
        )

# Create singleton instance
permission_service = PermissionService()