from app.core.database.pocketbase_client import pb
from app.core.schemas.department import DepartmentCreate, DepartmentUpdate
from app.inventory.models.department import Department


class DepartmentService:
    collection = "vms_i61b74n38e_departments"

    @classmethod
    def list(cls):
        records = pb.collection(cls.collection).get_full_list()
        return [Department(r) for r in records]

    @classmethod
    def get(cls, id: str):
        record = pb.collection(cls.collection).get_one(id)
        return Department(record)

    @classmethod
    def create(cls, data: DepartmentCreate):
        record = pb.collection(cls.collection).create(data.dict())
        return Department(record)

    @classmethod
    def update(cls, id: str, data: DepartmentUpdate):
        record = pb.collection(cls.collection).update(
            id, data.dict(exclude_unset=True))
        return Department(record)

    @classmethod
    def delete(cls, id: str):
        pb.collection(cls.collection).delete(id)
        return {"message": "Deleted"}
