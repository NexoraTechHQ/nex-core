
import logging
from app.core.schemas.role import RoleCreate, RoleUpdate
from app.core.services.base_service import BaseService

logger = logging.getLogger(__name__)

class RoleService(BaseService[RoleCreate]):
    def __init__(self):
        super().__init__(
            collection_name="permissions",
            create_schema=RoleCreate,
            update_schema=RoleUpdate
        )

# Create singleton instance
role_service = RoleService()