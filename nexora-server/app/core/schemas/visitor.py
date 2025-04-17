from pydantic import BaseModel
from typing import Optional, List


class VisitorCreate(BaseModel):
    name: str
    email: str
    images: Optional[List[str]] = None  # For URLs; files handled separately
    is_deleted: Optional[bool] = False


class VisitorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    images: Optional[List[str]] = None  # For URLs; files handled separately
    is_deleted: Optional[bool] = None
