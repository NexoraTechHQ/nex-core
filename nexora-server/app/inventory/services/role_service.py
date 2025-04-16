from app.core.schemas.role import RoleCreate, RoleUpdate
from app.core.database.pocketbase_client import pb
from app.core.database.tenant_manager import resolve_collection


class RoleService:
    @staticmethod
    def _expand_permissions(permission_field, tenant_id: str) -> list[dict]:
        # If already expanded (list of dicts), return as-is
        if isinstance(permission_field, list) and all(isinstance(p, dict) for p in permission_field):
            return [{"id": p["id"], "name": p.get("name", "")} for p in permission_field]

        # Otherwise fetch manually from permission collection
        permissions = []
        collection = resolve_collection("permissions", tenant_id)
        for pid in permission_field:
            try:
                p = pb.collection(collection).get_one(pid)
                permissions.append({"id": p["id"], "name": p.get("name", "")})
            except:
                continue
        return permissions

    @classmethod
    def list(cls, query_params, tenant_id: str):
        collection = resolve_collection("roles", tenant_id)
        raw = pb.collection(collection).get_list(query_params)
        for item in raw.get("items", []):
            if "permissions" in item:
                item["permissions"] = cls._expand_permissions(
                    item["permissions"], tenant_id)
        return raw

    @classmethod
    def get(cls, id: str, tenant_id: str):
        collection = resolve_collection("roles", tenant_id)
        record = pb.collection(collection).get_one(id)
        if "permissions" in record:
            record["permissions"] = cls._expand_permissions(
                record["permissions"], tenant_id)
        return record

    @classmethod
    def create(cls, data: RoleCreate, tenant_id: str):
        collection = resolve_collection("roles", tenant_id)
        return pb.collection(collection).create(data.model_dump())

    @classmethod
    def update(cls, id: str, data: RoleUpdate, tenant_id: str):
        collection = resolve_collection("roles", tenant_id)
        return pb.collection(collection).update(id, data.model_dump(exclude_unset=True))

    @classmethod
    def delete(cls, id: str, tenant_id: str):
        collection = resolve_collection("roles", tenant_id)
        pb.collection(collection).delete(id)
        return {"message": "Role deleted"}
