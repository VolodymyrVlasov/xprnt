import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class CompanyCreate(BaseModel):
    edrpou_code: str
    name: str
    itn_code: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    email: Optional[EmailStr] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    company_type_id: Optional[uuid.UUID] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    email: Optional[EmailStr] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    contact_user_id: Optional[uuid.UUID] = None
    company_type_id: Optional[uuid.UUID] = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    edrpou_code: str
    itn_code: Optional[str] = None
    name: str
    address1: Optional[str] = None
    address2: Optional[str] = None
    email: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    contact_user_id: Optional[uuid.UUID] = None
    company_type_id: Optional[uuid.UUID] = None
