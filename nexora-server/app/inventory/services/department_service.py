import logging
from app.core.schemas.department import DepartmentCreate, DepartmentUpdate
from app.core.services.base_service import BaseService

logger = logging.getLogger(__name__)

class DepartmentService(BaseService[DepartmentCreate]):
    def __init__(self):
        super().__init__(
            collection_name="departments",
            create_schema=DepartmentCreate,
            update_schema=DepartmentUpdate
        )

# Create singleton instance
department_service = DepartmentService()