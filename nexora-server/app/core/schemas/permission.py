from pydantic import BaseModel


class PermissionCreate(BaseModel):
    name: str


class PermissionUpdate(BaseModel):
    name: str | None = None
