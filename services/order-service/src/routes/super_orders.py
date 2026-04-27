import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, require_role
from src.models.order import OrderStatus, SuperOrderStatus
from src.models.user import Users
from src.repository.order import order_number_repo, order_repo
from src.repository.super_order import super_order_repo
from src.schemas.super_order import (
    SuperOrderAddOrder,
    SuperOrderCreate,
    SuperOrderResponse,
    SuperOrderStatusUpdate,
    SuperOrderUpdate,
)

router = APIRouter(prefix="/super-orders", tags=["super-orders"])

_TERMINAL_STATUSES = {OrderStatus.canceled, OrderStatus.returned}


@router.post("/", response_model=SuperOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_super_order(
    data: SuperOrderCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    order_num = await order_number_repo.create_number(db)
    obj = await super_order_repo.create(
        db,
        {
            "order_number_id": order_num.id,
            "company_id": data.company_id,
            "contact_user_id": data.contact_user_id,
            "payment_type_id": data.payment_type_id,
            "currency": data.currency,
            "billing_period_start": data.billing_period_start,
            "billing_period_end": data.billing_period_end,
        },
    )
    return await super_order_repo.get(db, obj.id)


@router.get("/", response_model=list[SuperOrderResponse])
async def list_super_orders(
    skip: int = 0,
    limit: int = 20,
    company_id: Optional[uuid.UUID] = None,
    status: Optional[SuperOrderStatus] = None,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await super_order_repo.get_all(db, skip=skip, limit=limit, company_id=company_id, status=status)


@router.get("/{super_order_id}", response_model=SuperOrderResponse)
async def get_super_order(
    super_order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await super_order_repo.get(db, super_order_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SuperOrder not found")
    return obj


@router.put("/{super_order_id}", response_model=SuperOrderResponse)
async def update_super_order(
    super_order_id: uuid.UUID,
    data: SuperOrderUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await super_order_repo.get(db, super_order_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SuperOrder not found")
    updated = await super_order_repo.update(db, obj, data.model_dump(exclude_none=True))
    return await super_order_repo.get(db, updated.id)


@router.post("/{super_order_id}/orders", response_model=SuperOrderResponse)
async def add_order_to_super_order(
    super_order_id: uuid.UUID,
    data: SuperOrderAddOrder,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    super_order = await super_order_repo.get(db, super_order_id)
    if not super_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SuperOrder not found")

    order = await order_repo.get(db, data.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.company_id != super_order.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must belong to the same company as the super order",
        )
    if order.status in _TERMINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add a canceled or returned order to a super order",
        )
    if order.super_order_id and order.super_order_id != super_order_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order already belongs to another super order",
        )

    result = await super_order_repo.add_order(db, super_order_id, data.order_id)
    return result


@router.delete("/{super_order_id}/orders/{order_id}", response_model=SuperOrderResponse)
async def remove_order_from_super_order(
    super_order_id: uuid.UUID,
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    super_order = await super_order_repo.get(db, super_order_id)
    if not super_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SuperOrder not found")
    if super_order.status != SuperOrderStatus.open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only remove orders from an open super order",
        )
    result = await super_order_repo.remove_order(db, super_order_id, order_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return result


@router.put("/{super_order_id}/status", response_model=SuperOrderResponse)
async def change_super_order_status(
    super_order_id: uuid.UUID,
    data: SuperOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    super_order = await super_order_repo.get(db, super_order_id)
    if not super_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SuperOrder not found")

    current = super_order.status
    new = data.status

    # Validate transitions
    allowed = False
    if new == SuperOrderStatus.cancelled and current == SuperOrderStatus.open:
        allowed = True
    elif current == SuperOrderStatus.open and new == SuperOrderStatus.invoiced:
        if not super_order.invoice_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invoiceNumber must be set before transitioning to invoiced",
            )
        allowed = True
    elif current == SuperOrderStatus.invoiced and new in (SuperOrderStatus.paid, SuperOrderStatus.open):
        allowed = True
    elif current == SuperOrderStatus.paid and new == SuperOrderStatus.closed:
        allowed = True

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{current}' to '{new}'",
        )

    updated = await super_order_repo.update(db, super_order, {"status": new})
    return await super_order_repo.get(db, updated.id)
