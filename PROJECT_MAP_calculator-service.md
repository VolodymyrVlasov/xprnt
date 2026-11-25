# PROJECT MAP — calculator-service
_Last updated: 2026-05-13_

## Service overview
| Item | Value |
|---|---|
| Location | services/calculator-service/ |
| Runtime | Python 3.x / FastAPI (unpinned — latest at install time) |
| Database | None |
| Cache | None |
| API prefix | /calculate |
| Dev port | Not exposed in docker-compose.dev.yml (no container defined) |
| Health | GET /health → {"status": "ok", "service": "calculator-service"} |
| Docs | /docs, /redoc |
| Status | Stub — price calculation returns hardcoded zero |

## File index
| File | Responsibility |
|---|---|
| services/calculator-service/app/config.py | Pydantic settings — ALLOWED_ORIGINS, ORDER_SERVICE_URL |
| services/calculator-service/app/main.py | FastAPI app factory, CORS middleware, router registration, /health |
| services/calculator-service/app/routes/calculator.py | Single POST /calculate endpoint |
| services/calculator-service/app/schemas/calculator.py | SizeInput, CalculatorRequest, CartItemDraft, CalculateResponse |
| services/calculator-service/app/services/calculator.py | calculate() — fetches product names from order_client, builds CartItemDraft stub |
| services/calculator-service/app/services/order_client.py | get_product() — returns hardcoded stub dict (HTTP call not implemented) |

## Endpoints

### /calculate
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /calculate | Calculate price for a configured item; returns CartItemDraft | No | — |

Request body (CalculatorRequest):
```json
{
  "size": { "diameter": null, "radius": null, "width": null, "height": null },
  "materialProductId": "uuid",
  "coatingProductId": "uuid",
  "cutTypeId": "uuid",
  "quantity": 100
}
```

Response body (CalculateResponse → CartItemDraft):
```json
{
  "cartItemDraft": {
    "categoryId": "00000000-0000-0000-0000-000000000000",
    "cartItemType": "configured",
    "name": "ЗАГЛУШКА\n· Матеріал: ...\n· Покриття: ...\n...",
    "shortName": "...",
    "amount": 100.0,
    "totalPrice": "0.00",
    "pricedAt": "<utcnow>"
  }
}
```

## Services / Business logic
| File | Method | Description |
|---|---|---|
| app/services/calculator.py | calculate | Calls order_client.get_product for material, coating, cut; builds name/shortName strings; returns totalPrice=0.00 (STUB) |
| app/services/order_client.py | get_product | Returns {"name": "Stub product", "id": "<uuid>"} — HTTP call to order-service NOT implemented |

## Config / Env vars
| Var | Default | Purpose |
|---|---|---|
| ALLOWED_ORIGINS | ["http://localhost:3000", "http://localhost:5173"] | CORS allowed origins |
| ORDER_SERVICE_URL | http://localhost:8000 | Base URL for order-service HTTP calls (not yet used) |

## External services
| Service | Used for | Files | Status |
|---|---|---|---|
| order-service (HTTP) | Fetch product names for calculation | app/services/order_client.py | NOT implemented — returns stub |

## Requirements
```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
httpx
pytest
pytest-asyncio
```
(All unpinned — versions resolved at container build time)

## Known issues and TODOs
| Location | Note |
|---|---|
| app/services/order_client.py | get_product() is a hardcoded stub — HTTP call to order-service with real product data is not implemented |
| app/services/calculator.py | totalPrice is hardcoded to Decimal("0.00") — no actual price calculation logic |
| app/services/calculator.py | categoryId is hardcoded to zero UUID — must be resolved from a real category |
| app/config.py | ORDER_SERVICE_URL is defined but never used |
| requirements.txt | All packages unpinned — may cause non-reproducible builds |
| docker-compose.dev.yml | No calculator-service container defined — service is standalone only |

## What is NOT implemented
| Feature | Status |
|---|---|
| Actual price calculation | totalPrice always returns 0.00 |
| Product data fetching from order-service | get_product returns stub; httpx import present but unused |
| Area-based calculation from SizeInput | SizeInput fields parsed but not used in calculation |
| Authentication | No auth dependency on /calculate |
| Docker compose integration | Service has no container in dev or prod compose files |
