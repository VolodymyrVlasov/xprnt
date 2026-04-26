import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, require_role
from src.models.order import Orders
from src.models.payment import PaymentStatus
from src.models.user import Users
from src.repository.order import order_repo
from src.repository.payment import payment_repo
from src.schemas.payment import PaymentCreate, PaymentResponse, PaymentStatusUpdate

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def register_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    # Validate referenced order exists if provided
    if data.order_id:
        order = await order_repo.get(db, data.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    payment = await payment_repo.create(
        db,
        {
            "payment_type_id": data.payment_type_id,
            "super_order_id": data.super_order_id,
            "amount": data.amount,
            "currency": data.currency,
            "fiscal_receipt_number": data.fiscal_receipt_number,
            "status": PaymentStatus.pending,
        },
    )

    # Attach payment to order if order_id provided
    if data.order_id:
        order = await order_repo.get(db, data.order_id)
        await order_repo.update(db, order, {"payment_id": payment.id})

    return payment


@router.get("/", response_model=list[PaymentResponse])
async def list_payments(
    order_id: Optional[uuid.UUID] = None,
    super_order_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    if super_order_id:
        return await payment_repo.get_by_super_order(db, super_order_id)
    if order_id:
        # Payments don't have a direct order_id column — find via orders.payment_id
        order = await order_repo.get(db, order_id)
        if not order or not order.payment_id:
            return []
        payment = await payment_repo.get(db, order.payment_id)
        return [payment] if payment else []
    return await payment_repo.get_all(db, limit=50)


@router.get("/{id}", response_model=PaymentResponse)
async def get_payment(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await payment_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return obj


@router.put("/{id}/status", response_model=PaymentResponse)
async def update_payment_status(
    id: uuid.UUID,
    data: PaymentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await payment_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return await payment_repo.update(db, obj, {"status": data.status})
