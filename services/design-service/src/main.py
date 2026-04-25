from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="design-service",
    description="xprnt Design Service — handles design files and previews",
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

# from src.routes import designs, uploads
# app.include_router(designs.router, prefix="/designs", tags=["designs"])
# app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "design-service"}
