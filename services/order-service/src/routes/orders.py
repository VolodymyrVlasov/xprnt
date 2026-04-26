import uuid
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db, require_role
from src.models.order import CommentEntityType, OrderStatus
from src.models.payment import PaymentStatus
from src.models.user import Users
from src.repository.comment import comment_repo
from src.repository.delivery import delivery_repo
from src.repository.order import order_repo
from src.repository.payment import payment_repo
from src.schemas.comment import CommentResponse
from src.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from src.services.order import change_status, create_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_route(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return await create_order(db, data, current_user.id)


@router.get("/my", response_model=list[OrderResponse])
async def get_my_orders(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return await order_repo.get_by_customer(db, current_user.id, skip=skip, limit=limit)


@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    order_status: Optional[OrderStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    role_name = current_user.role.role if current_user.role else ""
    if role_name in ("manager", "admin", "prepress", "postpress"):
        if order_status:
            return await order_repo.get_by_status(db, order_status, skip=skip, limit=limit)
        return await order_repo.get_all(db, skip=skip, limit=limit)
    return await order_repo.get_by_company(db, current_user.company_id, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    order = await order_repo.get_with_details(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    role_name = current_user.role.role if current_user.role else ""
    if role_name not in ("manager", "admin", "prepress", "postpress") and order.company_id != current_user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def change_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(require_role("manager", "admin", "prepress", "postpress")),
):
    role_name = current_user.role.role if current_user.role else "manager"
    return await change_status(db, order_id, data, role=role_name)


@router.post("/{order_id}/delivery", response_model=OrderResponse)
async def attach_delivery(
    order_id: uuid.UUID,
    delivery_id: uuid.UUID = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    order = await order_repo.get(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    delivery = await delivery_repo.get(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return await order_repo.update(db, order, {"delivery_id": delivery_id})


@router.post("/{order_id}/payment", response_model=OrderResponse)
async def attach_payment(
    order_id: uuid.UUID,
    payment_id: uuid.UUID = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    order = await order_repo.get(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    payment = await payment_repo.get(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    updates: dict = {"payment_id": payment_id}
    # Auto-advance to paid if payment is already paid
    if payment.status == PaymentStatus.paid and order.status == OrderStatus.pending:
        updates["status"] = OrderStatus.paid

    return await order_repo.update(db, order, updates)


@router.get("/{order_id}/comments", response_model=list[CommentResponse])
async def get_order_comments(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    return await comment_repo.get_by_entity(db, CommentEntityType.order, order_id)
