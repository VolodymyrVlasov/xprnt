import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db, require_role
from src.models.order import OrderStatus
from src.models.user import Users
from src.repository.order import order_repo
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
    if role_name in ("manager", "admin"):
        if order_status:
            return await order_repo.get_by_status(db, order_status, skip=skip, limit=limit)
        return await order_repo.get_all(db, skip=skip, limit=limit)
    # Regular users see only their company orders
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
    if role_name not in ("manager", "admin") and order.company_id != current_user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def change_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(require_role("manager", "admin")),
):
    role_name = current_user.role.role if current_user.role else "manager"
    return await change_status(db, order_id, data, role=role_name)
