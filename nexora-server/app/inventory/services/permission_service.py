from app.core.schemas.permission import PermissionCreate, PermissionUpdate
from app.core.database.pocketbase_client import pb
from app.core.database.tenant_manager import resolve_collection


class PermissionService:
    @classmethod
    def list(cls, query_params, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).get_list(query_params)

    @classmethod
    def get(cls, id: str, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).get_one(id)

    @classmethod
    def create(cls, data: PermissionCreate, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).create(data.model_dump())

    @classmethod
    def update(cls, id: str, data: PermissionUpdate, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).update(id, data.model_dump(exclude_unset=True))

    @classmethod
    def delete(cls, id: str, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        pb.collection(collection).delete(id)
        return {"message": "Permission deleted"}
