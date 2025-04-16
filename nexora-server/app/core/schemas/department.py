from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DepartmentOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    disabled: Optional[bool]
    created: Optional[datetime]
    updated: Optional[datetime]
