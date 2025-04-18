import logging
from typing import TypeVar, Generic, Type, Optional
from app.core.database.pocketbase_client import pb
from app.core.database.tenant_manager import resolve_collection
from app.shared.exceptions import NotFoundException, InternalServerException, BadRequestException
from pydantic import BaseModel
from app.shared.utils.response import sanitize_response, sanitize_record

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)  # For Pydantic schemas


class BaseService(Generic[T]):
    def __init__(self, collection_name: str, create_schema: Type[T], update_schema: Type[T]):
        self.pb = pb
        self.collection_name = collection_name
        self.create_schema = create_schema
        self.update_schema = update_schema

    def list(self, query_params: dict, tenant_id: str) -> dict:
        """List records with PocketBase-style pagination and filtering"""
        try:
            collection = resolve_collection(self.collection_name, tenant_id)
            logger.debug(
                f"Listing records for tenant {tenant_id} in collection {collection} with params: {query_params}")
            result = self.pb.collection(collection).get_list(**query_params)
            response = {
                "page": result.get("page", 1),
                "perPage": result.get("perPage", 10),
                "totalItems": result.get("totalItems", 0),
                "totalPages": result.get("totalPages", 0),
                "items": result.get("items", [])
            }
            logger.debug(f"Records listed: {response}")
            return sanitize_response(response)
        except Exception as e:
            logger.error(
                f"Failed to list records for tenant {tenant_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch records: {str(e)}")

    def get(self, id: str, tenant_id: str, query_params: Optional[dict] = None) -> dict:
        """Get a single record by ID with optional expand and fields"""
        try:
            collection = resolve_collection(self.collection_name, tenant_id)
            logger.debug(
                f"Fetching record {id} for tenant {tenant_id} in collection {collection} with params: {query_params}")
            record = self.pb.collection(collection).get_one(id, query_params)
            return sanitize_record(record)
        except Exception as e:
            logger.error(
                f"Failed to fetch record {id} for tenant {tenant_id}: {str(e)}")
            raise NotFoundException("Record not found")

    def create(self, data: T, tenant_id: str, query_params: Optional[dict] = None) -> dict:
        """Create a new record"""
        try:
            collection = resolve_collection(self.collection_name, tenant_id)
            data_dict = data.model_dump()
            logger.debug(
                f"Creating record for tenant {tenant_id} in collection {collection}: {data_dict}")
            # Debug the create method signature
            create_method = self.pb.collection(collection).create
            logger.debug(
                f"Create method signature: {create_method.__code__.co_varnames[:create_method.__code__.co_argcount]}")
            # Call create with only body_params
            record = self.pb.collection(collection).create(data_dict)
            return sanitize_record(record)
        except Exception as e:
            logger.error(
                f"Failed to create record for tenant {tenant_id}: {str(e)}")
            raise BadRequestException(f"Failed to create record: {str(e)}")

    def update(self, id: str, data: T, tenant_id: str, query_params: Optional[dict] = None) -> dict:
        """Update an existing record"""
        try:
            collection = resolve_collection(self.collection_name, tenant_id)
            data_dict = data.model_dump(exclude_unset=True)
            logger.debug(
                f"Updating record {id} for tenant {tenant_id} in collection {collection}: {data_dict}")
            # Call update with only id and body_params
            record = self.pb.collection(collection).update(id, data_dict)
            return sanitize_record(record)
        except Exception as e:
            logger.error(
                f"Failed to update record {id} for tenant {tenant_id}: {str(e)}")
            raise BadRequestException(f"Failed to update record: {str(e)}")

    def delete(self, id: str, tenant_id: str) -> dict:
        """Delete a record"""
        try:
            collection = resolve_collection(self.collection_name, tenant_id)
            logger.debug(
                f"Deleting record {id} for tenant {tenant_id} in collection {collection}")
            self.pb.collection(collection).delete(id)
            return {}
        except Exception as e:
            logger.error(
                f"Failed to delete record {id} for tenant {tenant_id}: {str(e)}")
            raise NotFoundException("Record not found")
