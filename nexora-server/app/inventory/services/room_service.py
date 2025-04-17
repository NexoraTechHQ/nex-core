import logging
from app.core.schemas.room import RoomCreate, RoomUpdate
from app.core.services.base_service import BaseService

logger = logging.getLogger(__name__)

class RoomService(BaseService[RoomCreate]):
    def __init__(self):
        super().__init__(
            collection_name="rooms",
            create_schema=RoomCreate,
            update_schema=RoomUpdate
        )

# Create singleton instance
room_service = RoomService()