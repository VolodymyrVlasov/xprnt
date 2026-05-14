import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, get_current_user, require_role
from src.models.user import Users
from src.repository.reference import (
    delivery_type_repo,
    measurement_unit_repo,
    payment_type_repo,
    role_repo,
    seller_repo,
    size_repo,
    team_repo,
)
from src.schemas.reference import (
    DeliveryTypeCreate,
    DeliveryTypeResponse,
    DeliveryTypeUpdate,
    MeasurementUnitCreate,
    MeasurementUnitResponse,
    PaymentTypeCreate,
    PaymentTypeResponse,
    PaymentTypeUpdate,
    RoleCreate,
    RoleResponse,
    SellerCreate,
    SellerResponse,
    SellerUpdate,
    SizeCreate,
    SizeResponse,
    SizeUpdate,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
)

router = APIRouter(prefix="/references", tags=["references"])


# ── Roles ──────────────────────────────────────────────────────────────────

@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(db: AsyncSession = Depends(get_db)):
    return await role_repo.get_all(db, limit=100)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("admin")),
):
    return await role_repo.create(db, {"role": data.role})


# ── Delivery Types ─────────────────────────────────────────────────────────

@router.get("/delivery-types", response_model=list[DeliveryTypeResponse])
async def list_delivery_types(db: AsyncSession = Depends(get_db)):
    return await delivery_type_repo.get_all(db, limit=100)


@router.post("/delivery-types", response_model=DeliveryTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_type(
    data: DeliveryTypeCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await delivery_type_repo.create(db, data.model_dump())


@router.get("/delivery-types/{id}", response_model=DeliveryTypeResponse)
async def get_delivery_type(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    obj = await delivery_type_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery type not found")
    return obj


@router.put("/delivery-types/{id}", response_model=DeliveryTypeResponse)
async def update_delivery_type(
    id: uuid.UUID,
    data: DeliveryTypeUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await delivery_type_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery type not found")
    return await delivery_type_repo.update(db, obj, data.model_dump(exclude_none=True))


# ── Payment Types ──────────────────────────────────────────────────────────

@router.get("/payment-types", response_model=list[PaymentTypeResponse])
async def list_payment_types(db: AsyncSession = Depends(get_db)):
    return await payment_type_repo.get_all(db, limit=100)


@router.post("/payment-types", response_model=PaymentTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_type(
    data: PaymentTypeCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await payment_type_repo.create(db, data.model_dump())


@router.get("/payment-types/{id}", response_model=PaymentTypeResponse)
async def get_payment_type(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    obj = await payment_type_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment type not found")
    return obj


@router.put("/payment-types/{id}", response_model=PaymentTypeResponse)
async def update_payment_type(
    id: uuid.UUID,
    data: PaymentTypeUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await payment_type_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment type not found")
    return await payment_type_repo.update(db, obj, data.model_dump(exclude_none=True))


# ── Sellers ────────────────────────────────────────────────────────────────

@router.get("/sellers", response_model=list[SellerResponse])
async def list_sellers(db: AsyncSession = Depends(get_db)):
    return await seller_repo.get_all(db, limit=100)


@router.post("/sellers", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
async def create_seller(
    data: SellerCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("admin")),
):
    return await seller_repo.create(db, data.model_dump())


@router.get("/sellers/{id}", response_model=SellerResponse)
async def get_seller(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    obj = await seller_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    return obj


@router.put("/sellers/{id}", response_model=SellerResponse)
async def update_seller(
    id: uuid.UUID,
    data: SellerUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("admin")),
):
    obj = await seller_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    return await seller_repo.update(db, obj, data.model_dump(exclude_none=True))


# ── Measurement Units ──────────────────────────────────────────────────────

@router.get("/measurement-units", response_model=list[MeasurementUnitResponse])
async def list_measurement_units(db: AsyncSession = Depends(get_db)):
    return await measurement_unit_repo.get_all(db, limit=100)


@router.post("/measurement-units", response_model=MeasurementUnitResponse, status_code=status.HTTP_201_CREATED)
async def create_measurement_unit(
    data: MeasurementUnitCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await measurement_unit_repo.create(db, data.model_dump())


# ── Sizes ──────────────────────────────────────────────────────────────────

@router.get("/sizes", response_model=list[SizeResponse])
async def list_sizes(unit_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)):
    if unit_id:
        return await size_repo.get_by_unit(db, unit_id)
    return await size_repo.get_all(db, limit=200)


@router.post("/sizes", response_model=SizeResponse, status_code=status.HTTP_201_CREATED)
async def create_size(
    data: SizeCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await size_repo.create(db, data.model_dump())


@router.get("/sizes/{id}", response_model=SizeResponse)
async def get_size(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    obj = await size_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")
    return obj


@router.put("/sizes/{id}", response_model=SizeResponse)
async def update_size(
    id: uuid.UUID,
    data: SizeUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await size_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")
    return await size_repo.update(db, obj, data.model_dump(exclude_none=True))


# ── Teams ──────────────────────────────────────────────────────────────────

@router.get("/teams", response_model=list[TeamResponse])
async def list_teams(db: AsyncSession = Depends(get_db)):
    return await team_repo.get_all(db, limit=100)


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("admin")),
):
    return await team_repo.create(db, data.model_dump())


@router.put("/teams/{id}", response_model=TeamResponse)
async def update_team(
    id: uuid.UUID,
    data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("admin")),
):
    obj = await team_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return await team_repo.update(db, obj, data.model_dump(exclude_none=True))
