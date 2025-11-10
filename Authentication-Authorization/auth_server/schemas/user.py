from typing import List, Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    roles: List[str]

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    roles: List[str]

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    message: str

class UserList(BaseModel):
    users: List[UserInDB]