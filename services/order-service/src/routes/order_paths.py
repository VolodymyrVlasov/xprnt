import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, require_role
from src.models.user import Users
from src.repository.order import order_repo
from src.repository.order_path import order_path_repo
from src.schemas.order_path import OrderPathCreate, OrderPathResponse, OrderPathUpdate

router = APIRouter(prefix="/order-paths", tags=["order-paths"])


@router.post("/", response_model=OrderPathResponse, status_code=status.HTTP_201_CREATED)
async def create_order_path(
    data: OrderPathCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "prepress", "admin")),
):
    order = await order_repo.get(db, data.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    existing = await order_path_repo.get_by_order(db, data.order_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Order path already exists for this order"
        )
    return await order_path_repo.create_for_order(db, data.order_id, data.path, data.docs_path)


@router.get("/order/{order_id}", response_model=OrderPathResponse)
async def get_order_path_by_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "prepress", "postpress", "admin")),
):
    obj = await order_path_repo.get_by_order(db, order_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order path not found")
    return obj


@router.put("/{order_path_id}", response_model=OrderPathResponse)
async def update_order_path(
    order_path_id: uuid.UUID,
    data: OrderPathUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "prepress", "admin")),
):
    obj = await order_path_repo.get(db, order_path_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order path not found")
    return await order_path_repo.update(db, obj, data.model_dump(exclude_none=True))
