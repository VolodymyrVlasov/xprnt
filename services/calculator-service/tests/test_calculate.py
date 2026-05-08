"""Tests for POST /calculate."""
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

_VALID_REQUEST = {
    "size": {"width": 210.0, "height": 297.0},
    "materialProductId": str(uuid.uuid4()),
    "coatingProductId": str(uuid.uuid4()),
    "cutTypeId": str(uuid.uuid4()),
    "quantity": 100,
}


def _stub_get_product(product_id):
    return {"name": "Stub product", "id": str(product_id)}


async def test_calculate_returns_200_with_correct_shape():
    with patch(
        "app.services.calculator.order_client.get_product",
        side_effect=AsyncMock(side_effect=_stub_get_product),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/calculate", json=_VALID_REQUEST)

    assert response.status_code == 200
    data = response.json()

    assert "cartItemDraft" in data
    draft = data["cartItemDraft"]

    assert draft["cartItemType"] == "configured"
    assert isinstance(draft["name"], str) and len(draft["name"]) > 0
    assert isinstance(draft["shortName"], str) and len(draft["shortName"]) > 0
    assert draft["amount"] == 100.0
    assert Decimal(draft["totalPrice"]) == Decimal("0.00")
    assert "pricedAt" in draft
    assert draft["categoryId"] == "00000000-0000-0000-0000-000000000000"


async def test_calculate_calls_order_client_for_all_three_products():
    mock_get = AsyncMock(side_effect=_stub_get_product)

    with patch("app.services.calculator.order_client.get_product", mock_get):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/calculate", json=_VALID_REQUEST)

    assert response.status_code == 200
    # called once each for material, coating, cut
    assert mock_get.call_count == 3
