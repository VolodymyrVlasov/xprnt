import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROLE = os.getenv("ROLE", "vps")

app = FastAPI(
    title="sync-service",
    description=f"xprnt Sync Service — synchronizes print jobs (role: {ROLE})",
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

# from src.routes import sync
# app.include_router(sync.router, prefix="/sync", tags=["sync"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "sync-service", "role": ROLE}
