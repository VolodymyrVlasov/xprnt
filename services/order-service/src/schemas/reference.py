import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    role: str


class RoleCreate(BaseModel):
    role: str


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: Optional[str] = None


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DeliveryTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None


class DeliveryTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None


class DeliveryTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict] = None


class PaymentTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None
    bank_requisite_id: Optional[uuid.UUID] = None
    transaction_fee: Optional[Decimal] = None


class PaymentTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None
    bank_requisite_id: Optional[uuid.UUID] = None
    transaction_fee: Optional[Decimal] = None


class PaymentTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict] = None
    bank_requisite_id: Optional[uuid.UUID] = None
    transaction_fee: Optional[Decimal] = None


class SellerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_type_id: uuid.UUID
    name: str
    short_name: Optional[str] = None


class SellerCreate(BaseModel):
    company_type_id: uuid.UUID
    name: str
    short_name: Optional[str] = None


class SellerUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    company_type_id: Optional[uuid.UUID] = None


class MeasurementUnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    measurement_unit: str
    classifier: Optional[str] = None


class MeasurementUnitCreate(BaseModel):
    measurement_unit: str
    classifier: Optional[str] = None


class SizeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    unit_id: uuid.UUID
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    radius: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    t_shirt_size_eu: Optional[str] = None
    t_shirt_size_age: Optional[str] = None
    roll_width: Optional[Decimal] = None


class SizeCreate(BaseModel):
    unit_id: uuid.UUID
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    radius: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    t_shirt_size_eu: Optional[str] = None
    t_shirt_size_age: Optional[str] = None
    roll_width: Optional[Decimal] = None


class SizeUpdate(BaseModel):
    unit_id: Optional[uuid.UUID] = None
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    radius: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    t_shirt_size_eu: Optional[str] = None
    t_shirt_size_age: Optional[str] = None
    roll_width: Optional[Decimal] = None
