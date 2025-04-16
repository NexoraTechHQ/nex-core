from app.core.database.pocketbase_client import pb
from app.core.database.tenant_manager import resolve_collection


class Permission:
    @staticmethod
    def create(data: dict, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).create(data)

    @staticmethod
    def update(id: str, data: dict, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).update(id, data)

    @staticmethod
    def delete(id: str, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        pb.collection(collection).delete(id)
        return {"message": "Permission deleted"}

    @staticmethod
    def get_list(query_params: dict, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).get_list(query_params)

    @staticmethod
    def get(id: str, tenant_id: str):
        collection = resolve_collection("permissions", tenant_id)
        return pb.collection(collection).get_one(id)
