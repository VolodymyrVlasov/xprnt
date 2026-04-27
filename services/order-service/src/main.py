import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.database import engine
from src.routes import auth, cart, categories, companies, orders, products, users
from src.routes import comments, deliveries, payments, references
from src.routes import price_multipliers, prices
from src.routes import super_orders, order_paths
from src.seeds import seed_admin_user, seed_reference_data

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await seed_reference_data()
    await seed_admin_user()
    logger.info("✅ xprnt order-service ready")
    yield


class UnicodeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title="order-service",
    description="xprnt Order Service — manages customer print orders",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    json_encoders={},
)

app.router.default_response_class = UnicodeJSONResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(companies.router, prefix=PREFIX)
app.include_router(products.router, prefix=PREFIX)
app.include_router(categories.router, prefix=PREFIX)
app.include_router(cart.router, prefix=PREFIX)
app.include_router(orders.router, prefix=PREFIX)
app.include_router(references.router, prefix=PREFIX)
app.include_router(prices.router, prefix=PREFIX)
app.include_router(price_multipliers.router, prefix=PREFIX)
app.include_router(deliveries.router, prefix=PREFIX)
app.include_router(payments.router, prefix=PREFIX)
app.include_router(comments.router, prefix=PREFIX)
app.include_router(super_orders.router, prefix=PREFIX)
app.include_router(order_paths.router, prefix=PREFIX)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "order-service"}
