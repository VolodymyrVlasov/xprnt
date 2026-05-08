import uuid
from typing import Any, Dict

import httpx

from app.config import settings


async def get_product(product_id: uuid.UUID) -> Dict[str, Any]:
    # TODO: use real response when order-service has data
    return {"name": "Stub product", "id": str(product_id)}
