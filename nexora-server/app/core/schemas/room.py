from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoomCreate(BaseModel):
    name: str
    department_id: str


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    department_id: Optional[str] = None


class RoomOut(BaseModel):
    id: str
    name: str
    department_id: Optional[dict]
    disabled: Optional[bool] = False
    created: Optional[datetime]
    updated: Optional[datetime]
