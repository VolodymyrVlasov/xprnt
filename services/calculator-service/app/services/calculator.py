import uuid
from datetime import datetime
from decimal import Decimal

from app.schemas.calculator import CalculateResponse, CalculatorRequest, CartItemDraft
from app.services import order_client


async def calculate(request: CalculatorRequest) -> CalculateResponse:
    material = await order_client.get_product(request.materialProductId)
    coating = await order_client.get_product(request.coatingProductId)
    cut = await order_client.get_product(request.cutTypeId)

    name = (
        f"ЗАГЛУШКА\n"
        f"· Матеріал: {material['name']}\n"
        f"· Покриття: {coating['name']}\n"
        f"· Різка: {cut['name']}\n"
        f"· Кількість: {request.quantity} шт."
    )
    short_name = f"{material['name']} {coating['name']} ({request.quantity} шт.)"

    draft = CartItemDraft(
        categoryId=uuid.UUID("00000000-0000-0000-0000-000000000000"),  # stub
        cartItemType="configured",
        name=name,
        shortName=short_name,
        amount=float(request.quantity),
        totalPrice=Decimal("0.00"),
        pricedAt=datetime.utcnow(),
    )

    return CalculateResponse(cartItemDraft=draft)
