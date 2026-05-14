import json
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes.design import router as design_router
from app.utils.file_storage import MinIOClient

logger = logging.getLogger(__name__)


class UnicodeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # MinIO — ensure buckets exist
    minio = MinIOClient()
    try:
        minio.ensure_buckets()
        logger.info("MinIO buckets ready")
    except Exception as exc:
        logger.error("MinIO init failed: %s", exc)
    app.state.minio = minio

    # Redis
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.redis = redis
    logger.info("✅ xprnt design-service ready")
    yield

    await redis.aclose()


app = FastAPI(
    title="xprnt Design Service",
    description="xprnt Design Service — handles design files and previews",
    version="1.0.0",
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

app.include_router(design_router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "design-service"}
