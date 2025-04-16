from app.core.schemas.tag import TagCreate, TagUpdate
from app.core.database.pocketbase_client import pb
from app.core.database.tenant_manager import resolve_collection


class TagService:
    @classmethod
    def list(cls, query_params, tenant_id: str):
        collection = resolve_collection("tags", tenant_id)
        return pb.collection(collection).get_list(query_params)

    @classmethod
    def get(cls, id: str, tenant_id: str):
        collection = resolve_collection("tags", tenant_id)
        return pb.collection(collection).get_one(id)

    @classmethod
    def create(cls, data: TagCreate, tenant_id: str):
        collection = resolve_collection("tags", tenant_id)
        return pb.collection(collection).create(data.dict())

    @classmethod
    def update(cls, id: str, data: TagUpdate, tenant_id: str):
        collection = resolve_collection("tags", tenant_id)
        return pb.collection(collection).update(id, data.dict(exclude_unset=True))

    @classmethod
    def delete(cls, id: str, tenant_id: str):
        collection = resolve_collection("tags", tenant_id)
        pb.collection(collection).delete(id)
        return {"message": "Tag deleted"}
