from app.core.schemas.room import RoomCreate, RoomUpdate
from app.core.database.pocketbase_client import pb
from app.core.database.tenant_manager import resolve_collection


class RoomService:
    @staticmethod
    def _expand_department(department_id: str, tenant_id: str) -> list[dict]:
        """
        Expand a single department_id string into a list containing one dict with 'id' and 'name'.
        """
        if isinstance(department_id, dict):
            return [{"id": department_id["id"], "name": department_id.get("name", "")}]

        if not department_id or not isinstance(department_id, str):
            return []

        try:
            collection = resolve_collection("departments", tenant_id)
            dept = pb.collection(collection).get_one(department_id)
            return [{"id": dept["id"], "name": dept.get("name", "")}]
        except Exception:
            return []

    @classmethod
    def list(cls, query_params: dict, tenant_id: str) -> dict:
        collection = resolve_collection("rooms", tenant_id)
        raw = pb.collection(collection).get_list(query_params)

        for item in raw.get("items", []):
            if "department_id" in item:
                item["department_id"] = cls._expand_department(
                    item["department_id"], tenant_id)

        return raw

    @classmethod
    def get(cls, id: str, tenant_id: str) -> dict:
        collection = resolve_collection("rooms", tenant_id)
        record = pb.collection(collection).get_one(id)

        if "department_id" in record:
            record["department_id"] = cls._expand_department(
                record["department_id"], tenant_id)

        return record

    @classmethod
    def create(cls, data: RoomCreate, tenant_id: str) -> dict:
        collection = resolve_collection("rooms", tenant_id)
        return pb.collection(collection).create(data.model_dump())

    @classmethod
    def update(cls, id: str, data: RoomUpdate, tenant_id: str) -> dict:
        collection = resolve_collection("rooms", tenant_id)
        return pb.collection(collection).update(id, data.model_dump(exclude_unset=True))

    @classmethod
    def delete(cls, id: str, tenant_id: str) -> dict:
        collection = resolve_collection("rooms", tenant_id)
        pb.collection(collection).delete(id)
        return {"message": "Room deleted"}
