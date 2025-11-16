from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str
    roles: Optional[List[str]] = ["user"]  # Default to "user" role if not specified

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    roles: List[str]

    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('roles', mode='before')
    @classmethod
    def convert_roles(cls, v: Any) -> List[str]:
        # Handle both list of strings and list of Role objects
        if v and isinstance(v, list):
            if len(v) > 0 and hasattr(v[0], 'name'):
                return [role.name for role in v]
        return v

class UserResponse(BaseModel):
    message: str

class UserList(BaseModel):
    users: List[UserInDB]