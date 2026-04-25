import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import Users
from src.repository.company import company_repo
from src.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    return await company_repo.get_all(db, skip=skip, limit=limit)


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    existing = await company_repo.get_by_edrpou(db, data.edrpou_code)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Company with this EDRPOU already exists")
    return await company_repo.create(db, data.model_dump())


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    company = await company_repo.get(db, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    company = await company_repo.get(db, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await company_repo.update(db, company, data.model_dump(exclude_none=True))
