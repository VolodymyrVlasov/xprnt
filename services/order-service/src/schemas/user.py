import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    name: str
    middlename: Optional[str] = None
    lastname: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    email: EmailStr
    telegram: Optional[str] = None


class UserCreate(UserBase):
    password: str
    company_id: uuid.UUID
    role_id: uuid.UUID


class UserUpdate(BaseModel):
    name: Optional[str] = None
    middlename: Optional[str] = None
    lastname: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    telegram: Optional[str] = None
    team_id: Optional[uuid.UUID] = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    middlename: Optional[str] = None
    lastname: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    telegram: Optional[str] = None
    company_id: uuid.UUID
    role_id: uuid.UUID
    team_id: Optional[uuid.UUID] = None
    role: Optional[RoleResponse] = None
