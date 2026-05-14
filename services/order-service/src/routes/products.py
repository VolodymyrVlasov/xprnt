import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db, require_role
from src.models.user import Users
from src.repository.product import product_repo
from src.schemas.import_products import ImportReport
from src.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from src.services.import_service import ImportService
from src.services.product import create_product, deactivate_product, update_product
from src.utils.import_parser import parse_csv, parse_xlsx

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[uuid.UUID] = None,
    in_stock: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    return await product_repo.get_filtered(db, skip=skip, limit=limit, category_id=category_id, in_stock=in_stock)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_route(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await create_product(db, data)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    product = await product_repo.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product_route(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await update_product(db, product_id, data)


@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await deactivate_product(db, product_id)


MAX_IMPORT_SIZE = 5 * 1024 * 1024  # 5 MB

SUPPORTED_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@router.post("/import", response_model=ImportReport)
async def import_products(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    content = await file.read()
    if len(content) > MAX_IMPORT_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (max 5 MB)")

    content_type = (file.content_type or "").split(";")[0].strip()
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {content_type}. Use text/csv or .xlsx",
        )

    try:
        if content_type in ("text/csv", "application/csv"):
            rows = parse_csv(content)
        else:
            rows = parse_xlsx(content)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    service = ImportService(db)
    return await service.import_products(rows)
