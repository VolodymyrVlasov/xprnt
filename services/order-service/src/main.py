from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="order-service",
    description="xprnt Order Service — manages customer print orders",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# from src.routes import orders, auth
# app.include_router(orders.router, prefix="/orders", tags=["orders"])
# app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "order-service"}
