from pydantic import BaseModel
from typing import Optional, List


class UserOfTenantCreate(BaseModel):
    name: str
    email: str
    system_user_id: str  # this is relation to collection system_users
    images: Optional[List[str]] = None  # For URLs; files handled separately
    is_deleted: Optional[bool] = False


class UserOfTenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    system_user_id: str  # this is relation to collection system_users, NOT ALLOW TO CHANGE THIS
    images: Optional[List[str]] = None  # For URLs; files handled separately
    is_deleted: Optional[bool] = None
