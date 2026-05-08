import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes.calculator import router as calculator_router

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


app = FastAPI(
    title="xprnt Calculator Service",
    description="xprnt Calculator Service — price and cart item estimation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.router.default_response_class = UnicodeJSONResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculator_router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "calculator-service"}
