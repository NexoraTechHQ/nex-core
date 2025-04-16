from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RoleCreate(BaseModel):
    name: str
    permissions: List[str]


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleOut(BaseModel):
    id: str
    name: str
    permissions: Optional[List[dict]]
    disabled: Optional[bool]
    created: Optional[datetime]
    updated: Optional[datetime]
