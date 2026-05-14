import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cart import CartStatus
from src.models.order import OrderStatus, Orders
from src.repository.cart import cart_repo
from src.repository.order import order_number_repo, order_repo
from src.schemas.order import OrderCreate, OrderStatusUpdate

# Role-based status transitions
# Each role maps current status → list of allowed next statuses
_STATUS_TRANSITIONS: dict[str, dict[OrderStatus, list[OrderStatus]]] = {
    "manager": {
        OrderStatus.pending:          [OrderStatus.paid, OrderStatus.canceled],
        OrderStatus.paid:             [OrderStatus.execution, OrderStatus.canceled],
        OrderStatus.execution:        [OrderStatus.printing, OrderStatus.canceled],
        OrderStatus.printing:         [OrderStatus.printed, OrderStatus.canceled],
        OrderStatus.printed:          [OrderStatus.postprint, OrderStatus.canceled],
        OrderStatus.postprint:        [OrderStatus.done, OrderStatus.waiting_delivery, OrderStatus.canceled],
        OrderStatus.done:             [OrderStatus.successful, OrderStatus.waiting_delivery],
        OrderStatus.waiting_delivery: [OrderStatus.shipped, OrderStatus.canceled],
        OrderStatus.shipped:          [OrderStatus.successful, OrderStatus.returned],
        OrderStatus.successful:       [],
        OrderStatus.canceled:         [],
        OrderStatus.returned:         [],
    },
    "prepress": {
        OrderStatus.execution:  [OrderStatus.printing],
        OrderStatus.printing:   [OrderStatus.printed],
        # all other statuses: no transitions allowed
        **{s: [] for s in OrderStatus if s not in (OrderStatus.execution, OrderStatus.printing)},
    },
    "postpress": {
        OrderStatus.printed:    [OrderStatus.postprint],
        OrderStatus.postprint:  [OrderStatus.done, OrderStatus.waiting_delivery],
        **{s: [] for s in OrderStatus if s not in (OrderStatus.printed, OrderStatus.postprint)},
    },
    "admin": {s: list(OrderStatus) for s in OrderStatus},
}


async def create_order(db: AsyncSession, data: OrderCreate, current_user_id: uuid.UUID) -> Orders:
    cart = await cart_repo.get_with_items(db, data.cart_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if cart.status != CartStatus.locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cart must be locked before ordering"
        )
    if await order_repo.get_by_cart(db, data.cart_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order already exists for this cart")

    order_num = await order_number_repo.create_number(db, created_by=current_user_id)

    from src.repository.user import user_repo

    user = await user_repo.get(db, current_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    order = await order_repo.create(
        db,
        {
            "order_number_id": order_num.id,
            "cart_id": data.cart_id,
            "seller_id": data.seller_id,
            "customer_id": current_user_id,
            "payment_user_id": current_user_id,
            "delivery_user_id": current_user_id,
            "company_id": user.company_id,
            "status": OrderStatus.pending,
            "total_price": cart.total_price,
            "currency": data.currency,
        },
    )

    await cart_repo.update(db, cart, {"status": CartStatus.ordered})
    return order


async def change_status(
    db: AsyncSession, order_id: uuid.UUID, data: OrderStatusUpdate, role: str
) -> Orders:
    order = await order_repo.get(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    allowed = _STATUS_TRANSITIONS.get(role, {}).get(order.status, [])
    if data.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role}' cannot change status from '{order.status}' to '{data.status}'",
        )

    return await order_repo.update(db, order, {"status": data.status})
